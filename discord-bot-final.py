#!/usr/bin/env python3
"""
Discord bot for CLAWTEX - Spawns own Kiro session
Simple approach: Each Discord message spawns clawtex agent
"""
import discord
import asyncio
import os
import sys
import subprocess
import re

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not DISCORD_BOT_TOKEN:
    print("Error: DISCORD_BOT_TOKEN not set")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ WOPR online: {client.user}', flush=True)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    await message.add_reaction("👀")
    
    async with message.channel.typing():
        try:
            # Run Kiro with clawtex agent
            result = subprocess.run(
                ['kiro-cli', 'chat', '--agent', 'clawtex', '--message', message.content],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.expanduser('~')
            )
            
            response = result.stdout.strip()
            
            # Clean ANSI codes
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            response = ansi_escape.sub('', response)
            
            # Extract actual response (skip prompts)
            lines = response.split('\n')
            clean_lines = [l for l in lines if l and not l.startswith('[clawtex]') and not l.startswith('All tools')]
            response = '\n'.join(clean_lines).strip()
            
            if response:
                # Split long messages
                if len(response) > 1900:
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response)
            else:
                await message.channel.send("💪 Back to work!")
                
        except subprocess.TimeoutExpired:
            await message.channel.send("⏱️ Timeout - task taking longer than expected")
        except Exception as e:
            await message.channel.send(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
