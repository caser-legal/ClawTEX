#!/usr/bin/env python3
"""
Discord bot for CLAWTEX - Simple direct response pattern
"""
import discord
import asyncio
import sys
import os
import requests

# Bot token from environment
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not DISCORD_BOT_TOKEN:
    print("Error: DISCORD_BOT_TOKEN environment variable not set")
    sys.exit(1)

# Gateway API endpoint (if we want to route through gateway)
GATEWAY_URL = "http://localhost:8080/message"  # We'll use direct approach instead

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Discord bot logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore own messages
    if message.author == client.user:
        return
    
    # Add eyes reaction (OpenClaw style)
    await message.add_reaction("👀")
    
    async with message.channel.typing():
        # For now, echo back - we'll connect to Kiro session next
        response = f"WOPR received: {message.content}"
        await message.channel.send(response)

if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
