#!/usr/bin/env python3
"""
Discord Channel Adapter for CLAWTEX Gateway
Routes Discord messages to/from persistent Kiro session
EXACTLY like OpenClaw
"""
import discord
import asyncio
import os
import sys
import json
import uuid
from pathlib import Path

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not DISCORD_BOT_TOKEN:
    print("Error: DISCORD_BOT_TOKEN not set")
    sys.exit(1)

GATEWAY_QUEUE = Path.home() / ".kiro" / "gateway_queue.jsonl"
GATEWAY_RESPONSES = Path.home() / ".kiro" / "gateway_responses.jsonl"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

pending_responses = {}

@client.event
async def on_ready():
    print(f'✅ Discord adapter online: {client.user}', flush=True)
    # Start response monitor
    client.loop.create_task(monitor_responses())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # OpenClaw style: eyes reaction
    await message.add_reaction("👀")
    
    async with message.channel.typing():
        # Generate response ID
        response_id = str(uuid.uuid4())
        
        # Queue message to gateway
        queue_message = {
            'response_id': response_id,
            'message': message.content,
            'source': 'discord',
            'channel_id': str(message.channel.id),
            'author': str(message.author.name)
        }
        
        with open(GATEWAY_QUEUE, 'a') as f:
            f.write(json.dumps(queue_message) + '\n')
        
        # Store pending response
        pending_responses[response_id] = message.channel
        
        # Wait for response (with timeout)
        for _ in range(60):  # 60 seconds max
            await asyncio.sleep(1)
            if response_id in pending_responses and pending_responses[response_id] == "DONE":
                break

async def monitor_responses():
    """Monitor gateway responses and send to Discord"""
    while True:
        try:
            if GATEWAY_RESPONSES.exists():
                with open(GATEWAY_RESPONSES, 'r') as f:
                    lines = f.readlines()
                
                # Clear file
                GATEWAY_RESPONSES.write_text('')
                
                for line in lines:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    response_id = data.get('response_id')
                    response_text = data.get('response')
                    channel_id = data.get('channel_id')
                    
                    # Handle docked messages (no specific response_id)
                    if response_id == "docked" and channel_id:
                        channel = client.get_channel(int(channel_id))
                        if channel:
                            if len(response_text) > 1900:
                                chunks = [response_text[i:i+1900] for i in range(0, len(response_text), 1900)]
                                for chunk in chunks:
                                    await channel.send(chunk)
                            else:
                                await channel.send(response_text if response_text else "💪 Back to work!")
                        continue
                    
                    # Handle regular responses
                    if response_id in pending_responses:
                        channel = pending_responses[response_id]
                        if isinstance(channel, discord.TextChannel):
                            # Send response
                            if len(response_text) > 1900:
                                chunks = [response_text[i:i+1900] for i in range(0, len(response_text), 1900)]
                                for chunk in chunks:
                                    await channel.send(chunk)
                            else:
                                await channel.send(response_text if response_text else "💪 Back to work!")
                        
                        pending_responses[response_id] = "DONE"
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"Response monitor error: {e}", file=sys.stderr)
            await asyncio.sleep(1)

if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
