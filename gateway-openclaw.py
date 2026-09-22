#!/usr/bin/env python3
"""
CLAWTEX Gateway - OpenClaw Architecture
- Persistent Kiro session (agent runtime)
- Discord channel adapter routes to session
- Lane-based queuing (serial by default)
- Heartbeat + cron system
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
import queue
import re

# Configuration
HEARTBEAT_INTERVAL = 900  # 15 minutes
WORKSPACE = Path.home() / ".kiro" / "workspace"
HEARTBEAT_FILE = WORKSPACE / "HEARTBEAT.md"
CRON_DIR = Path.home() / ".kiro" / "cron"
JOBS_FILE = CRON_DIR / "jobs.json"
RUNS_DIR = CRON_DIR / "runs"
LOG_FILE = Path.home() / ".kiro" / "logs" / "gateway.log"
PID_FILE = Path.home() / ".kiro" / "gateway.pid"
DEFAULT_TZ = "America/Los_Angeles"

# Global state
kiro_process = None
jobs = []
last_heartbeat = 0
message_queue = queue.Queue()  # Lane-based queue
discord_responses = {}  # Store responses for Discord
output_mode = "cli"  # "cli" or "discord"
discord_channel_id = os.getenv('DISCORD_CHANNEL_ID')  # For docking

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}\n"
    print(log_msg.strip())
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg)

def start_kiro_session():
    """Start persistent Kiro CLI session"""
    log("Starting Kiro CLI session...")
    
    try:
        process = pexpect.spawn(
            'kiro-cli chat --agent clawtex',
            encoding='utf-8',
            timeout=300,
            cwd=str(Path.home())
        )
        
        # Wait for ready
        process.expect([r'\[clawtex\].*λ.*>', pexpect.TIMEOUT], timeout=30)
        log("Kiro session ready")
        return process
        
    except Exception as e:
        log(f"Failed to start Kiro: {e}")
        return None

def send_to_session(message, response_id=None):
    """Send message to Kiro session and capture response"""
    global kiro_process, output_mode, discord_channel_id
    
    if not kiro_process:
        return None
    
    # Check for dock/undock commands
    if message.strip() == "dock-discord":
        if discord_channel_id:
            output_mode = "discord"
            return "✅ Docked to Discord - all responses will go to Discord channel"
        else:
            return "❌ DISCORD_CHANNEL_ID not set - cannot dock"
    
    if message.strip() == "undock":
        output_mode = "cli"
        return "✅ Undocked - responses back to CLI"
    
    try:
        kiro_process.sendline(message)
        kiro_process.expect([r'\[clawtex\].*λ.*>', pexpect.TIMEOUT], timeout=60)
        
        response = kiro_process.before
        
        # Clean ANSI codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        response = ansi_escape.sub('', response).strip()
        
        # Route based on output mode
        if output_mode == "discord" and discord_channel_id:
            # Send to Discord
            GATEWAY_RESPONSES = Path.home() / ".kiro" / "gateway_responses.jsonl"
            with open(GATEWAY_RESPONSES, 'a') as f:
                f.write(json.dumps({
                    'response_id': 'docked',
                    'response': response,
                    'channel_id': discord_channel_id
                }) + '\n')
            log("Response routed to Discord (docked mode)")
        
        # Store for Discord if response_id provided
        if response_id:
            discord_responses[response_id] = response
        
        return response
        
    except pexpect.TIMEOUT:
        log("Session timeout")
        return None
    except Exception as e:
        log(f"Session error: {e}")
        return None

def process_message_queue():
    """Process messages serially (lane-based queuing)"""
    global message_queue
    
    GATEWAY_QUEUE = Path.home() / ".kiro" / "gateway_queue.jsonl"
    GATEWAY_RESPONSES = Path.home() / ".kiro" / "gateway_responses.jsonl"
    
    while True:
        try:
            # Check file-based queue
            if GATEWAY_QUEUE.exists():
                with open(GATEWAY_QUEUE, 'r') as f:
                    lines = f.readlines()
                
                if lines:
                    # Clear queue file
                    GATEWAY_QUEUE.write_text('')
                    
                    for line in lines:
                        if not line.strip():
                            continue
                        
                        msg_data = json.loads(line)
                        message = msg_data.get('message')
                        response_id = msg_data.get('response_id')
                        source = msg_data.get('source', 'unknown')
                        
                        log(f"Processing message from {source}: {message[:50]}...")
                        response = send_to_session(message, response_id)
                        
                        if response and response_id:
                            # Write response
                            with open(GATEWAY_RESPONSES, 'a') as f:
                                f.write(json.dumps({
                                    'response_id': response_id,
                                    'response': response
                                }) + '\n')
                            log(f"Response written for {response_id}")
            
            time.sleep(0.5)
            
        except Exception as e:
            log(f"Queue processing error: {e}")
            time.sleep(1)

# Start queue processor thread
threading.Thread(target=process_message_queue, daemon=True).start()

def cleanup(signum=None, frame=None):
    """Cleanup on exit"""
    global kiro_process
    log("Gateway shutting down...")
    
    if kiro_process:
        kiro_process.close()
    
    if PID_FILE.exists():
        PID_FILE.unlink()
    
    sys.exit(0)

def main():
    global kiro_process, last_heartbeat
    
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Write PID
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    
    log("CLAWTEX Gateway started (OpenClaw architecture)")
    log(f"Heartbeat interval: {HEARTBEAT_INTERVAL}s")
    log(f"Default timezone: {DEFAULT_TZ}")
    
    # Start Kiro session
    kiro_process = start_kiro_session()
    if not kiro_process:
        log("Failed to start - exiting")
        cleanup()
    
    last_heartbeat = time.time()
    
    # Main loop
    try:
        while True:
            current_time = time.time()
            
            # Heartbeat check
            if current_time - last_heartbeat >= HEARTBEAT_INTERVAL:
                message_queue.put({
                    'message': 'HEARTBEAT CHECK',
                    'source': 'heartbeat'
                })
                last_heartbeat = current_time
            
            time.sleep(60)
            
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
