# CLAWTEX - Shell Aliases
# OpenClaw × CORTEX
# Add to ~/.zshrc

# Start CLAWTEX agent
alias claw="~/.kiro/clawtex"
alias clawtex="~/.kiro/clawtex"

# Quick memory access
alias claw-memory="cat ~/.kiro/workspace/memory/$(date +%Y-%m-%d).md"
alias claw-anchor="cat ~/.kiro/workspace/memory/anchor.md"
alias claw-soul="cat ~/.kiro/workspace/SOUL.md"

# Edit workspace files
alias claw-edit-soul="vim ~/.kiro/workspace/SOUL.md"
alias claw-edit-user="vim ~/.kiro/workspace/USER.md"
alias claw-edit-anchor="vim ~/.kiro/workspace/memory/anchor.md"

# Verification
alias claw-verify="~/.kiro/verify.sh"

# View logs (if using MCP servers)
alias claw-logs="tail -f ~/.kiro/logs/*.log 2>/dev/null || echo 'No logs found'"

# Stop MCP servers (if using DORY)
alias claw-quit="pkill -f 'mcp-server' ; pkill -f 'context7-mcp' ; echo '🦞 CLAWTEX stopped'"
