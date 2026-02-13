#!/bin/bash
echo "🦞 CLAWTEX - Verification"
echo "OpenClaw × CORTEX"
echo "=================================="
echo ""

echo "✓ Core workspace files:"
ls -1 ~/.kiro/workspace/{SOUL,AGENTS,USER,IDENTITY,TOOLS,HEARTBEAT}.md 2>/dev/null | sed 's|.*/||'

echo ""
echo "✓ Tiered memory system:"
ls -1 ~/.kiro/workspace/memory/{anchor.md,semantic.json,procedural.md,2026-02-12.md} 2>/dev/null | sed 's|.*/||'

echo ""
echo "✓ Skills:"
ls -1 ~/.kiro/workspace/skills/ 2>/dev/null | head -5
echo "   ... ($(ls ~/.kiro/workspace/skills/ 2>/dev/null | wc -l | tr -d ' ') total)"

echo ""
echo "✓ PULSE prompts:"
ls -1 ~/.kiro/prompts/{1,2,3}.md 2>/dev/null | sed 's|.*/||'

echo ""
echo "✓ Agent config:"
if [ -f ~/.kiro/agents/openclaw.json ]; then
    echo "   openclaw.json ($(jq -r '.hooks.agentSpawn | length' ~/.kiro/agents/openclaw.json) hooks configured)"
else
    echo "   ❌ Missing openclaw.json"
fi

echo ""
echo "=================================="
echo "🚀 Ready to launch: kiro-cli chat --agent openclaw"
echo "   or just: claw / clawtex"
