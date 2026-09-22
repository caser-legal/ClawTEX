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
    
    # Route to Kiro gateway via stdin
    msg_text = f"[Discord:{message.author.name}] {message.content}"
    print(f"DISCORD_INBOUND:{msg_text}", flush=True)

async def process_outbound_messages():
    """Process messages from Kiro to Discord"""
    while True:
        try:
            channel_id, text = await outbound_queue.get()
            channel = client.get_channel(int(channel_id))
            if channel:
                await channel.send(text)
        except Exception as e:
            print(f"Error sending to Discord: {e}", file=sys.stderr)

def send_to_discord(channel_id: str, text: str):
    """Thread-safe way to send message to Discord from gateway"""
    asyncio.run_coroutine_threadsafe(
        outbound_queue.put((channel_id, text)),
        client.loop
    )

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
