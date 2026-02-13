#!/usr/bin/env python3
"""
Discord bot for CLAWTEX - Direct Kiro session integration
Routes Discord messages to/from persistent Kiro session
"""
import discord
import asyncio
import os
import sys
import pexpect

# Bot token from environment
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not DISCORD_BOT_TOKEN:
    print("Error: DISCORD_BOT_TOKEN environment variable not set")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Shared Kiro process (will be set by gateway)
kiro_process = None
active_channel = None

def set_kiro_process(process):
    """Called by gateway to share Kiro process"""
    global kiro_process
    kiro_process = process

@client.event
async def on_ready():
    print(f'✅ WOPR online: {client.user}', flush=True)

@client.event
async def on_message(message):
    global active_channel
    
    # Ignore own messages
    if message.author == client.user:
        return
    
    # Add eyes reaction (OpenClaw style)
    await message.add_reaction("👀")
    
    async with message.channel.typing():
        # Save active channel for responses
        active_channel = message.channel
        
        if not kiro_process:
            await message.channel.send("⚠️ WOPR offline - Kiro session not connected")
            return
        
        try:
            # Send to Kiro session
            kiro_process.sendline(message.content)
            
            # Wait for response (match the prompt)
            kiro_process.expect([r'\[clawtex\].*λ.*>', pexpect.TIMEOUT], timeout=60)
            
            # Capture output
            response = kiro_process.before.decode('utf-8', errors='ignore')
            
            # Clean up response
            response = response.strip()
            
            # Remove ANSI codes
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            response = ansi_escape.sub('', response)
            
            # Send to Discord (split if too long)
            if len(response) > 1900:
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for chunk in chunks:
                    await message.channel.send(f"```\n{chunk}\n```")
            elif response:
                await message.channel.send(f"```\n{response}\n```")
            else:
                await message.channel.send("💪 Back to work!")
                
        except pexpect.TIMEOUT:
            await message.channel.send("⏱️ Response timeout - WOPR is thinking...")
        except Exception as e:
            await message.channel.send(f"❌ Error: {str(e)}")

async def send_to_discord(text):
    """Send message from Kiro to Discord (for heartbeats, cron jobs, etc)"""
    if active_channel:
        await active_channel.send(text)

if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
