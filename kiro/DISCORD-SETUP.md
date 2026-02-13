# Discord Bot Setup for CLAWTEX

## Overview

CLAWTEX gateway integrates Discord bot (WOPR) for remote messaging when you're away from terminal but Mac is still running - exactly like OpenClaw.

## Architecture

```
Discord Messages → discord-bot.py → gateway.py → Kiro Session
                                                      ↓
Discord ← gateway.py ← Kiro Response ←────────────────┘
```

## Setup Steps

### 1. Get Discord Bot Token

1. Go to https://discord.com/developers/applications
2. Create New Application (or use existing)
3. Go to "Bot" section
4. Copy the bot token
5. Enable "Message Content Intent" under Privileged Gateway Intents

### 2. Set Environment Variable

Add to `~/.zshrc`:

```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
export DISCORD_CHANNEL_ID="your_channel_id"  # Optional - specific channel only
```

Then reload:
```bash
source ~/.zshrc
```

### 3. Invite Bot to Server

Use this URL (replace CLIENT_ID with your Application ID):
```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=2048&scope=bot
```

Permissions needed: Send Messages (2048)

### 4. Restart Gateway

```bash
claw-stop
claw-start
```

## How It Works

### Inbound (Discord → Kiro)

1. User sends message in Discord
2. Bot receives via `on_message` event
3. Prints `DISCORD_INBOUND:[username] message` to stdout
4. Gateway monitors stdout, routes to Kiro session
5. Agent responds naturally

### Outbound (Kiro → Discord)

1. Cron job with `delivery.channel = "discord"` triggers
2. Gateway calls `send_to_discord(channel_id, text)`
3. Uses `asyncio.run_coroutine_threadsafe()` for thread-safe async
4. Bot sends message to Discord channel

### Cron Job Discord Delivery

```bash
python3 ~/.kiro/cron-cli.py add \
  --name "Daily standup" \
  --cron "0 9 * * *" \
  --session isolated \
  --message "Review overnight progress" \
  --delivery-mode announce
```

Then agent can update job to deliver to Discord:
```python
# Agent uses execute_bash to modify job
job['delivery']['channel'] = 'discord'
job['delivery']['to'] = 'CHANNEL_ID'
```

## Testing

1. Send message in Discord channel
2. Check gateway logs: `tail -f ~/.kiro/logs/gateway.log`
3. Should see: `Discord → Kiro: [username] message`
4. Agent should respond in Kiro session

## Troubleshooting

**Bot not responding:**
- Check `DISCORD_BOT_TOKEN` is set
- Verify bot has "Message Content Intent" enabled
- Check gateway logs for errors

**Messages not routing:**
- Ensure gateway is running: `claw-status`
- Check Discord bot process: `ps aux | grep discord-bot`
- Verify channel ID if using `DISCORD_CHANNEL_ID`

**Outbound not working:**
- Check cron job has `delivery.channel = "discord"`
- Verify `delivery.to` has valid channel ID
- Check bot has permission to send in that channel
