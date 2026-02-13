#!/usr/bin/env python3
"""
CLAWTEX Cron CLI - Manage cron jobs
Compatible with OpenClaw cron job format
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
import uuid

JOBS_FILE = Path.home() / ".kiro" / "cron" / "jobs.json"

def load_jobs():
    """Load jobs from storage"""
    if not JOBS_FILE.exists():
        return []
    
    with open(JOBS_FILE, "r") as f:
        data = json.load(f)
        return data.get("jobs", [])

def save_jobs(jobs):
    """Save jobs to storage"""
    JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JOBS_FILE, "w") as f:
        json.dump({"version": 1, "jobs": jobs}, f, indent=2)

def cmd_list(args):
    """List all cron jobs"""
    jobs = load_jobs()
    
    if not jobs:
        print("No cron jobs configured")
        return
    
    print(f"{'ID':<36} {'Name':<20} {'Schedule':<15} {'Enabled':<8}")
    print("-" * 85)
    
    for job in jobs:
        job_id = job.get("jobId", job.get("id", "unknown"))
        name = job.get("name", "Unnamed")[:20]
        schedule = job.get("schedule", {})
        kind = schedule.get("kind", "unknown")
        enabled = "Yes" if job.get("enabled", True) else "No"
        
        print(f"{job_id:<36} {name:<20} {kind:<15} {enabled:<8}")

def cmd_add(args):
    """Add a new cron job"""
    jobs = load_jobs()
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Build schedule
    schedule = {}
    if args.at:
        # Support human durations like "20m"
        if args.at.endswith('m') and args.at[:-1].isdigit():
            minutes = int(args.at[:-1])
            from datetime import timedelta
            target = datetime.now() + timedelta(minutes=minutes)
            schedule = {"kind": "at", "at": target.isoformat()}
        else:
            schedule = {"kind": "at", "at": args.at}
    elif args.every:
        schedule = {"kind": "every", "everyMs": args.every}
    elif args.cron:
        schedule = {"kind": "cron", "expr": args.cron, "tz": args.tz}
    else:
        print("Error: Must specify --at, --every, or --cron")
        sys.exit(1)
    
    # Build payload
    payload = {}
    if args.session == "main":
        if not args.system_event:
            print("Error: Main session jobs require --system-event")
            sys.exit(1)
        payload = {"kind": "systemEvent", "text": args.system_event}
    elif args.session == "isolated":
        if not args.message:
            print("Error: Isolated session jobs require --message")
            sys.exit(1)
        payload = {
            "kind": "agentTurn",
            "message": args.message,
            "timeoutSeconds": args.timeout
        }
    
    # Build delivery (isolated only)
    delivery = {}
    if args.session == "isolated":
        delivery = {"mode": args.delivery_mode}
    
    # Build job
    job = {
        "jobId": job_id,
        "name": args.name,
        "schedule": schedule,
        "sessionTarget": args.session,
        "wakeMode": args.wake,
        "payload": payload,
        "enabled": True,
        "lastRun": 0,
        "consecutiveFailures": 0
    }
    
    if delivery:
        job["delivery"] = delivery
    
    if args.delete_after_run:
        job["deleteAfterRun"] = True
    
    jobs.append(job)
    save_jobs(jobs)
    
    print(f"✅ Created cron job: {job_id}")
    print(f"   Name: {args.name}")
    print(f"   Schedule: {schedule.get('kind')}")
    print(f"   Wake mode: {args.wake}")
    if delivery:
        print(f"   Delivery: {delivery.get('mode')}")

def cmd_remove(args):
    """Remove a cron job"""
    jobs = load_jobs()
    
    jobs = [j for j in jobs if j.get("jobId") != args.job_id and j.get("id") != args.job_id]
    save_jobs(jobs)
    
    print(f"✅ Removed job: {args.job_id}")

def cmd_enable(args):
    """Enable a cron job"""
    jobs = load_jobs()
    
    for job in jobs:
        if job.get("jobId") == args.job_id or job.get("id") == args.job_id:
            job["enabled"] = True
            save_jobs(jobs)
            print(f"✅ Enabled job: {args.job_id}")
            return
    
    print(f"❌ Job not found: {args.job_id}")

def cmd_disable(args):
    """Disable a cron job"""
    jobs = load_jobs()
    
    for job in jobs:
        if job.get("jobId") == args.job_id or job.get("id") == args.job_id:
            job["enabled"] = False
            save_jobs(jobs)
            print(f"✅ Disabled job: {args.job_id}")
            return
    
    print(f"❌ Job not found: {args.job_id}")

def main():
    parser = argparse.ArgumentParser(description="CLAWTEX Cron Job Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List command
    subparsers.add_parser("list", help="List all cron jobs")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new cron job")
    add_parser.add_argument("--name", required=True, help="Job name")
    add_parser.add_argument("--at", help="One-shot time (ISO 8601 or duration like '20m')")
    add_parser.add_argument("--every", type=int, help="Interval in milliseconds")
    add_parser.add_argument("--cron", help="Cron expression (5-field)")
    add_parser.add_argument("--tz", default="America/Los_Angeles", help="Timezone (default: PST)")
    add_parser.add_argument("--session", choices=["main", "isolated"], required=True, help="Session target")
    add_parser.add_argument("--system-event", help="System event text (main session)")
    add_parser.add_argument("--message", help="Agent message (isolated session)")
    add_parser.add_argument("--wake", choices=["now", "next-heartbeat"], default="now", help="Wake mode (default: now)")
    add_parser.add_argument("--delete-after-run", action="store_true", help="Delete after successful run")
    add_parser.add_argument("--delivery-mode", choices=["announce", "none"], default="announce", help="Delivery mode for isolated jobs")
    add_parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds (default: 300)")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a cron job")
    remove_parser.add_argument("job_id", help="Job ID")
    
    # Enable command
    enable_parser = subparsers.add_parser("enable", help="Enable a cron job")
    enable_parser.add_argument("job_id", help="Job ID")
    
    # Disable command
    disable_parser = subparsers.add_parser("disable", help="Disable a cron job")
    disable_parser.add_argument("job_id", help="Job ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "list":
        cmd_list(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "remove":
        cmd_remove(args)
    elif args.command == "enable":
        cmd_enable(args)
    elif args.command == "disable":
        cmd_disable(args)

if __name__ == "__main__":
    main()
