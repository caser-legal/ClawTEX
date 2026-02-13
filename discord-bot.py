#!/usr/bin/env python3
"""
Discord bot for CLAWTEX - Routes messages between Discord and Kiro gateway
"""
import discord
import asyncio
import sys
import os

# Bot token from environment
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not DISCORD_TOKEN:
    print("Error: DISCORD_BOT_TOKEN environment variable not set")
    sys.exit(1)

# Channel ID where bot listens (optional - can listen to all channels)
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Message queue for outbound messages (from Kiro to Discord)
outbound_queue = asyncio.Queue()

@client.event
async def on_ready():
    print(f'✅ Discord bot logged in as {client.user}')
    # Start outbound message processor
    client.loop.create_task(process_outbound_messages())

@client.event
async def on_message(message):
    # Ignore own messages
    if message.author == client.user:
        return
    
    # Filter by channel if specified
    if DISCORD_CHANNEL_ID and str(message.channel.id) != DISCORD_CHANNEL_ID:
        return
    
    # Add eyes reaction + typing indicator (OpenClaw style)
    await message.add_reaction("👀")
    
    async with message.channel.typing():
        # Send to gateway with channel ID
        msg_text = f"{message.channel.id}|[Discord:{message.author.name}] {message.content}"
        print(f"DISCORD_INBOUND:{msg_text}", flush=True)
        
        # Keep typing for a bit while waiting for response
        await asyncio.sleep(2)

async def process_outbound_messages():
    """Process messages from Kiro to Discord"""
    while True:
        try:
            # Read from stdin for outbound messages
            import sys
            import select
            
            if select.select([sys.stdin], [], [], 0.1)[0]:
                line = sys.stdin.readline().strip()
                if line.startswith("SEND:"):
                    parts = line.replace("SEND:", "").split(":", 1)
                    if len(parts) == 2:
                        channel_id, text = parts
                        channel = client.get_channel(int(channel_id))
                        if channel:
                            await channel.send(text)
            
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in outbound: {e}", file=sys.stderr)

def send_to_discord(channel_id: str, text: str):
    """Thread-safe way to send message to Discord from gateway"""
    asyncio.run_coroutine_threadsafe(
        outbound_queue.put((channel_id, text)),
        client.loop
    )

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
