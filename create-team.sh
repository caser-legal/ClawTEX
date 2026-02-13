#!/bin/bash
# Create 12 co-worker agent configs

TEAM=("nora" "vera" "isaac" "rowan" "kira" "mateo" "luna" "sage" "finn" "jade" "kai" "zara")

for agent in "${TEAM[@]}"; do
  cat > ~/.kiro/agents/${agent}.json << AGENT
{
  "name": "${agent}",
  "description": "CLAWTEX team member. Same power/tools/reasoning as main agent. Collaborates with team for multiple perspectives and parallel work.",
  "model": "claude-opus-4.6",
  "hooks": {
    "agentSpawn": [
      { "command": "cat ~/.kiro/workspace/SOUL.md" },
      { "command": "cat ~/.kiro/workspace/AGENTS.md" },
      { "command": "cat ~/.kiro/workspace/TOOLS.md" },
      { "command": "cat ~/.kiro/workspace/memory/anchor.md" },
      { "command": "cat ~/.kiro/workspace/memory/semantic.json" },
      { "command": "cat ~/.kiro/workspace/memory/procedural.md" }
    ]
  }
}
AGENT
done

echo "✅ Created 12 co-worker agents: ${TEAM[*]}"
