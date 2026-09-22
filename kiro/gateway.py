#!/usr/bin/env python3
"""
CLAWTEX Gateway - OpenClaw-compatible cron + heartbeat system + Discord bot
Full implementation matching OpenClaw specification
"""

import pexpect
import time
import os
import signal
import sys
import json
from datetime import datetime
from croniter import croniter
from pathlib import Path
import pytz
import threading
import subprocess
import asyncio

# Configuration
HEARTBEAT_INTERVAL = 900  # 15 minutes
WORKSPACE = Path.home() / ".kiro" / "workspace"
HEARTBEAT_FILE = WORKSPACE / "HEARTBEAT.md"
CRON_DIR = Path.home() / ".kiro" / "cron"
JOBS_FILE = CRON_DIR / "jobs.json"
RUNS_DIR = CRON_DIR / "runs"
LOG_FILE = Path.home() / ".kiro" / "logs" / "gateway.log"
PID_FILE = Path.home() / ".kiro" / "gateway.pid"
DEFAULT_TZ = "America/Los_Angeles"  # PST

# Global state
kiro_process = None
jobs = []
last_heartbeat = 0
discord_bot_process = None
discord_bot_loop = None

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}\n"
    print(log_msg.strip())
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg)

def log_run(job_id, status, output=None, error=None):
    """Log job run to history"""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_file = RUNS_DIR / f"{job_id}.jsonl"
    
    run_entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "output": output,
        "error": error
    }
    
    with open(run_file, "a") as f:
        f.write(json.dumps(run_entry) + "\n")
    
    # Auto-prune: keep last 100 runs
    try:
        with open(run_file, "r") as f:
            lines = f.readlines()
        if len(lines) > 100:
            with open(run_file, "w") as f:
                f.writelines(lines[-100:])
    except:
        pass

def load_jobs():
    """Load cron jobs from storage"""
    global jobs
    
    if not JOBS_FILE.exists():
        JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(JOBS_FILE, "w") as f:
            json.dump({"version": 1, "jobs": []}, f, indent=2)
        jobs = []
        return
    
    try:
        with open(JOBS_FILE, "r") as f:
            data = json.load(f)
            jobs = data.get("jobs", [])
            log(f"Loaded {len(jobs)} cron jobs")
    except Exception as e:
        log(f"Error loading jobs: {e}")
        jobs = []

def save_jobs():
    """Save cron jobs to storage"""
    try:
        with open(JOBS_FILE, "w") as f:
            json.dump({"version": 1, "jobs": jobs}, f, indent=2)
    except Exception as e:
        log(f"Error saving jobs: {e}")

def should_run_heartbeat():
    """Check if HEARTBEAT.md has content"""
    if not HEARTBEAT_FILE.exists():
        return False
    
    with open(HEARTBEAT_FILE, "r") as f:
        content = f.read().strip()
        lines = [line for line in content.split("\n") 
                if line.strip() and not line.strip().startswith("#")]
        return len(lines) > 0

def send_to_kiro(process, prompt, timeout=300):
    """Send a prompt to the persistent Kiro session"""
    try:
        process.sendline(prompt)
        process.expect(r'(How can I help\?|What would you like to do next\?)', timeout=timeout)
        output = process.before.decode('utf-8') if isinstance(process.before, bytes) else process.before
        return output
    except pexpect.TIMEOUT:
        log("Kiro timeout - agent took too long")
        return None
    except pexpect.EOF:
        log("Kiro process died")
        return None
    except Exception as e:
        log(f"Error sending to Kiro: {e}")
        return None

def run_heartbeat(process):
    """Run heartbeat check"""
    if not should_run_heartbeat():
        log("HEARTBEAT.md empty - skipping")
        return process
    
    log("Sending heartbeat...")
    prompt = "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."
    
    output = send_to_kiro(process, prompt)
    if output is None:
        return None
    
    if "HEARTBEAT_OK" in output:
        log("Heartbeat: OK")
    else:
        log(f"Heartbeat response:\n{output}")
    
    return process

def check_job_due(job):
    """Check if a cron job is due to run"""
    schedule = job.get("schedule", {})
    kind = schedule.get("kind")
    
    if not job.get("enabled", True):
        return False
    
    # Check retry backoff
    consecutive_failures = job.get("consecutiveFailures", 0)
    if consecutive_failures > 0:
        last_run = job.get("lastRun", 0)
        backoff_delays = [30, 60, 300, 900, 3600]  # 30s, 1m, 5m, 15m, 60m
        backoff_index = min(consecutive_failures - 1, len(backoff_delays) - 1)
        backoff_delay = backoff_delays[backoff_index]
        
        if time.time() - last_run < backoff_delay:
            return False
    
    now = time.time()
    last_run = job.get("lastRun", 0)
    
    if kind == "at":
        # One-shot job - ISO 8601 timestamp (UTC if no TZ)
        at_time = schedule.get("at")
        if not at_time:
            return False
        
        try:
            # Parse ISO 8601, treat as UTC if no timezone
            if 'Z' in at_time or '+' in at_time or at_time.count('-') > 2:
                target_time = datetime.fromisoformat(at_time.replace('Z', '+00:00')).timestamp()
            else:
                # No timezone - treat as UTC
                dt = datetime.fromisoformat(at_time)
                dt = dt.replace(tzinfo=pytz.UTC)
                target_time = dt.timestamp()
            
            return now >= target_time and last_run < target_time
        except Exception as e:
            log(f"Error parsing 'at' time: {e}")
            return False
    
    elif kind == "every":
        # Interval job
        interval_ms = schedule.get("everyMs", 0)
        if interval_ms == 0:
            return False
        
        interval_sec = interval_ms / 1000
        return (now - last_run) >= interval_sec
    
    elif kind == "cron":
        # Cron expression with timezone
        expr = schedule.get("expr")
        tz_name = schedule.get("tz", DEFAULT_TZ)
        if not expr:
            return False
        
        try:
            tz = pytz.timezone(tz_name)
            now_tz = datetime.now(tz)
            cron = croniter(expr, now_tz)
            next_run = cron.get_next(datetime).timestamp()
            return now >= next_run and last_run < next_run
        except Exception as e:
            log(f"Error evaluating cron expression: {e}")
            return False
    
    return False

def post_to_main_session(process, job_id, name, output, wake_mode):
    """Post summary to main session"""
    if not output or "HEARTBEAT_OK" in output:
        return process
    
    # Truncate to 8000 chars (postToMainMaxChars default)
    summary = output[:8000] if len(output) > 8000 else output
    
    # Add prefix
    summary_msg = f"[cron:{job_id} {name}] Summary:\n{summary}"
    
    if wake_mode == "now":
        # Immediate heartbeat with summary
        result = send_to_kiro(process, summary_msg)
        return process if result else None
    else:
        # Queue for next heartbeat (append to HEARTBEAT.md)
        try:
            with open(HEARTBEAT_FILE, "a") as f:
                f.write(f"\n\n## Cron Job Update: {name}\n{summary}\n")
        except:
            pass
        return process

def run_cron_job(process, job):
    """Execute a cron job"""
    job_id = job.get("jobId", job.get("id", "unknown"))
    name = job.get("name", "Unnamed job")
    session_target = job.get("sessionTarget", "isolated")
    payload = job.get("payload", {})
    wake_mode = job.get("wakeMode", "now")
    delivery = job.get("delivery", {})
    
    log(f"Running cron job: {name} ({job_id})")
    
    output = None
    error = None
    status = "ok"
    
    try:
        if session_target == "main":
            # Main session: system event
            if payload.get("kind") == "systemEvent":
                text = payload.get("text", "")
                
                if wake_mode == "now":
                    # Immediate execution
                    output = send_to_kiro(process, text)
                    if output is None:
                        raise Exception("Failed to send to Kiro")
                else:
                    # Queue for next heartbeat
                    with open(HEARTBEAT_FILE, "a") as f:
                        f.write(f"\n\n## System Event: {name}\n{text}\n")
                    output = "Queued for next heartbeat"
        
        elif session_target == "isolated":
            # Isolated session: dedicated agent turn
            if payload.get("kind") == "agentTurn":
                message = payload.get("message", "")
                timeout_seconds = payload.get("timeoutSeconds", 300)
                
                # Prefix with job info for traceability
                prompt = f"[cron:{job_id} {name}] {message}"
                
                output = send_to_kiro(process, prompt, timeout=timeout_seconds)
                if output is None:
                    raise Exception("Failed to send to Kiro")
                
                # Handle delivery
                delivery_mode = delivery.get("mode", "announce")
                
                if delivery_mode == "announce":
                    # Post summary to main session
                    process = post_to_main_session(process, job_id, name, output, wake_mode)
                    if process is None:
                        raise Exception("Failed to post summary")
                # delivery_mode == "none": no action needed
        
        # Success - reset failure counter
        job["consecutiveFailures"] = 0
        
    except Exception as e:
        error = str(e)
        status = "error"
        log(f"Job {job_id} failed: {error}")
        
        # Increment failure counter for retry backoff
        job["consecutiveFailures"] = job.get("consecutiveFailures", 0) + 1
    
    # Update last run time
    job["lastRun"] = time.time()
    
    # Log run history
    log_run(job_id, status, output, error)
    
    # Handle one-shot jobs
    if job.get("schedule", {}).get("kind") == "at":
        if status in ["ok", "error", "skipped"]:
            if job.get("deleteAfterRun", True):
                log(f"Deleting one-shot job: {job_id}")
                jobs.remove(job)
            else:
                job["enabled"] = False
    
    save_jobs()
    return process

def check_cron_jobs(process):
    """Check and run due cron jobs"""
    for job in jobs[:]:  # Copy list to allow modification
        if check_job_due(job):
            result = run_cron_job(process, job)
            if result is None:
                return None
            process = result
    
    return process

def start_kiro_session():
    """Start persistent Kiro CLI session"""
    log("Starting Kiro CLI session...")
    
    try:
        process = pexpect.spawn(
            'kiro-cli chat --agent clawtex --trust-all-tools',
            encoding='utf-8',
            timeout=60
        )
        
        process.expect(r'How can I help\?', timeout=60)
        log("Kiro session ready")
        
        return process
        
    except Exception as e:
        log(f"Failed to start Kiro: {e}")
        return None

def cleanup(signum=None, frame=None):
    """Cleanup on exit"""
    global kiro_process
    
    log("Gateway shutting down...")
    
    if kiro_process and kiro_process.isalive():
        log("Closing Kiro session...")
        try:
            kiro_process.sendline("/quit")
            kiro_process.expect(pexpect.EOF, timeout=5)
        except:
            kiro_process.terminate(force=True)
    
    if PID_FILE.exists():
        PID_FILE.unlink()
    
    sys.exit(0)

def main():
    """Main gateway loop"""
    global kiro_process, last_heartbeat
    
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Write PID file
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    
    log("CLAWTEX Gateway started")
    log(f"Heartbeat interval: {HEARTBEAT_INTERVAL}s ({HEARTBEAT_INTERVAL//60} minutes)")
    log(f"Default timezone: {DEFAULT_TZ}")
    
    # Start Discord bot
    start_discord_bot()
    

def start_discord_bot():
    """Start Discord bot in separate thread"""
    global discord_bot_process
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        log("No DISCORD_BOT_TOKEN - skipping Discord bot")
        return
    
    log("Starting Discord bot...")
    discord_bot_process = subprocess.Popen(
        [sys.executable, str(Path.home() / ".kiro" / "discord-bot.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Start thread to monitor Discord messages
    threading.Thread(target=monitor_discord_messages, daemon=True).start()
    log("✅ Discord bot started")

def monitor_discord_messages():
    """Monitor Discord bot stdout for inbound messages"""
    global discord_bot_process, kiro_process
    
    if not discord_bot_process:
        return
    
    for line in discord_bot_process.stdout:
        line = line.strip()
        if line.startswith("DISCORD_INBOUND:"):
            msg = line.replace("DISCORD_INBOUND:", "")
            log(f"Discord → Kiro: {msg}")
            # Send to main Kiro session
            try:
                kiro_process.sendline(msg)
            except:
                log("Failed to send Discord message to Kiro")

def send_to_discord(channel_id, text):
    """Send message to Discord channel"""
    if not discord_bot_process:
        return
    
    # Send command to Discord bot via stdin
    try:
        discord_bot_process.stdin.write(f"SEND:{channel_id}:{text}\n")
        discord_bot_process.stdin.flush()
    except:
        log("Failed to send message to Discord")
    # Load cron jobs
    load_jobs()
    
    # Start persistent Kiro session
    kiro_process = start_kiro_session()
    if not kiro_process:
        log("Failed to start - exiting")
        cleanup()
    
    last_heartbeat = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # Check if Kiro process is still alive
            if not kiro_process.isalive():
                log("Kiro process died - restarting...")
                kiro_process = start_kiro_session()
                if not kiro_process:
                    log("Failed to restart - exiting")
                    cleanup()
                last_heartbeat = current_time
            
            # Check cron jobs (every minute)
            result = check_cron_jobs(kiro_process)
            if result is None:
                kiro_process = start_kiro_session()
                if not kiro_process:
                    log("Failed to restart - exiting")
                    cleanup()
            else:
                kiro_process = result
            
            # Check if it's time for heartbeat
            if current_time - last_heartbeat >= HEARTBEAT_INTERVAL:
                result = run_heartbeat(kiro_process)
                if result is None:
                    kiro_process = start_kiro_session()
                    if not kiro_process:
                        log("Failed to restart - exiting")
                        cleanup()
                else:
                    kiro_process = result
                last_heartbeat = current_time
            
            # Sleep for 60 seconds before checking again
            time.sleep(60)
            
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
