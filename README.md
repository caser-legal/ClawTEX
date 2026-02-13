# 🦞 CLAWTEX

**OpenClaw × CORTEX**  
**Built**: 2026-02-12  
**Status**: Ready for testing

---

## 🚀 Quick Start (60 seconds)

### 1. Install Aliases
```bash
cat ~/.kiro/aliases.sh >> ~/.zshrc
source ~/.zshrc
```

### 2. Launch CLAWTEX
```bash
clawtex
# or just: claw
```

### 3. The Agent Will:
- ✅ Show banner
- ✅ Load all workspace files (SOUL, AGENTS, memory, skills)
- ✅ Have full context before first message
- ✅ Decide autonomously when to deploy team and start loops
- ✅ Never ask "want me to start?" (acts when confident, explains when stuck)

### 4. Example Usage
```
You: "Fix the StoreKit trial eligibility in WaveA"

Agent: [Checks memory, sees StoreKit patterns, high confidence]
       Deploying team to research and fix...
       
       @nora: Researching StoreKit 2 patterns (2025/2026 docs)
       @vera: Auditing current implementation
       @isaac: Checking App Store guidelines
       @rowan: Reviewing WaveB implementation in /live/
       
       [Autonomous loop runs until complete]
       
       ✅ Fixed. Trial eligibility now uses isEligibleForIntroOffer.
       Verified against WaveB. Build passes, zero warnings.
```

### 5. How It Decides
**Acts autonomously when:**
- Seen this before (memory/)
- Request is clear ("fix X in Y")
- High confidence (patterns match)
- Knows quality bar (/live/* apps)

**Asks questions when:**
- Request is vague
- Multiple valid approaches
- Uncertain about outcome

**Never asks:** "want me to start?" or "should I continue?" — that's annoying.

---

## What is CLAWTEX?

A unified AI agent system combining the best of:
- **OpenClaw**: Workspace structure, SOUL/identity system, multi-agent
- **CORTEX (PULSE + DORY)**: Tiered memory, autonomous loops, tool orchestration

---

## Directory Structure

```
~/.kiro/
├── agents/
│   └── openclaw.json           # Main agent with workspace hooks
├── workspace/
│   ├── SOUL.md                 # Identity & philosophy (OpenClaw)
│   ├── AGENTS.md               # Behavior patterns (OpenClaw)
│   ├── USER.md                 # User context (OpenClaw)
│   ├── IDENTITY.md             # Agent identity (OpenClaw)
│   ├── TOOLS.md                # Device config (OpenClaw)
│   ├── HEARTBEAT.md            # Proactive checks (OpenClaw)
│   ├── memory/
│   │   ├── anchor.md           # Tier 0: 95% attention (PULSE)
│   │   ├── semantic.json       # Tier 1: 85% attention (PULSE)
│   │   ├── procedural.md       # Tier 2: 60% attention (PULSE)
│   │   └── YYYY-MM-DD.md       # Daily memory (OpenClaw)
│   ├── skills/                 # 24 skills from OpenClaw
│   │   └── ios-ops/
│   │       ├── SKILL.md
│   │       ├── references/
│   │       └── scripts/
│   └── agents/                 # Multi-agent (future: 12 + 1 overseer)
└── prompts/
    ├── 1.md                    # Initializer (PULSE)
    ├── 2.md                    # Coder (PULSE)
    └── 3.md                    # QA (PULSE)
```

---

## How It Works

### 1. Agent Spawn (Context Injection)
When you run `kiro-cli chat --agent openclaw`, the hooks automatically load:

```bash
# Core identity
SOUL.md → Who you are
AGENTS.md → How you behave
USER.md → Who you're helping
IDENTITY.md → Your name/emoji/vibe
TOOLS.md → Available tools/devices
HEARTBEAT.md → Proactive tasks

# Tiered memory (PULSE innovation)
anchor.md → MUST/NEVER rules (95% attention)
semantic.json → Facts/patterns (85% attention)
procedural.md → Code patterns (60% attention)
YYYY-MM-DD.md → Today's events
```

**Result**: Agent has FULL context before first message (like OpenClaw)

### 2. Tiered Memory System (PULSE)
```
🔴 anchor.md (95%)     - MUST/NEVER rules, project state
🟠 semantic.json (85%) - Facts, patterns, preferences
🟡 procedural.md (60%) - Code patterns, commands
📝 YYYY-MM-DD.md       - Daily events log
```

**Why better than OpenClaw**: Prioritizes by importance, not just chronological

### 3. Autonomous Loops (PULSE)
From SOUL.md:
> **Never stop until complete.** When given a task, work autonomously until 100% done.

From anchor.md:
> **Never stop until 100% complete** - Autonomous loops run until all features pass

**Why better than OpenClaw**: Truly autonomous, doesn't ask permission at every step

### 4. Skills System (OpenClaw)
```
skills/ios-ops/
├── SKILL.md                    # Main skill definition
├── references/
│   ├── swift6-concurrency.md
│   ├── storekit2-patterns.md
│   ├── ios-development-complete.md
│   └── deep-audit-methodology.md
└── scripts/
    └── audit_ios_project.sh
```

**Why better than DORY**: Self-documenting, human-readable, version-controllable

### 5. Multi-Agent (Future)
Plan: 12 co-workers + 1 overseer (13 total)
- Each agent has unique personality (USER.md, memory/)
- All share core knowledge (SOUL.md, AGENTS.md, TOOLS.md via symlinks)
- Overseer delegates tasks to specialists

---

## Usage

### Start the Agent
```bash
# Add to ~/.zshrc
alias claw="kiro-cli chat --agent openclaw"

# Start
claw
```

### The Agent Will:
1. Load all workspace files automatically
2. Read tiered memory (anchor → semantic → procedural → daily)
3. Have full context before responding
4. Work autonomously until tasks are 100% complete
5. Update memory files as it learns
6. Never stop mid-task to ask permission

### Memory Updates
The agent automatically appends to today's memory file when using memory tools.

You can manually update:
```bash
# Add to today's memory
echo "## Event\nDescription" >> ~/.kiro/workspace/memory/$(date +%Y-%m-%d).md

# Update anchor (MUST/NEVER rules)
vim ~/.kiro/workspace/memory/anchor.md

# Update semantic (facts/patterns)
vim ~/.kiro/workspace/memory/semantic.json

# Update procedural (code patterns)
vim ~/.kiro/workspace/memory/procedural.md
```

---

## What Makes This Special

### From OpenClaw
✅ **Workspace organization** - Clear separation of concerns  
✅ **SOUL.md** - "You're not a chatbot" philosophy  
✅ **Skills as markdown** - Self-documenting, human-readable  
✅ **Multi-agent** - Co-workers with personalities  
✅ **Daily memory** - Historical tracking  

### From PULSE
✅ **Tiered memory** - Prioritized by importance (95%, 85%, 60%)  
✅ **Autonomous loops** - Never stops until 100% complete  
✅ **Progress tracking** - Quantified completion (0-100%)  
✅ **Mode system** - Initializer (@1), Coder (@2), QA (@3)  

### From DORY
✅ **Hooks system** - Auto-inject context on spawn  
✅ **Tool orchestration** - Smart tool selection  
✅ **MCP integration** - Connect external tools  
✅ **Memory persistence** - Auto-append to daily files  

---

## The Magic

**OpenClaw's framework** provides the structure and personality.  
**PULSE's innovations** provide the autonomy and intelligence.  
**DORY's hooks** provide the integration glue.

**Result**: An agent that:
- Knows who it is (SOUL.md)
- Knows who you are (USER.md)
- Remembers everything (tiered memory)
- Works autonomously (PULSE loops)
- Never stops until done (anchor.md rules)
- Loads context automatically (hooks)
- Has specialized skills (ios-ops, etc.)

---

## Next Steps

1. **Test the agent**
   ```bash
   claw
   # Try: "Build an iOS app with SwiftUI"
   ```

2. **Create co-worker agents** (12 + 1 overseer)
   - Copy `openclaw.json` → `nora.json`, `vera.json`, etc.
   - Give each unique personality in their USER.md
   - Symlink shared files (SOUL.md, AGENTS.md, TOOLS.md)

3. **Connect to DORY** (optional)
   - Add MCP server config to openclaw.json
   - Get 44 tools from nvidia-cli

4. **Set up Discord bot** (optional)
   - Connect to Kiro agent
   - Get updates when you're away

5. **Add more skills**
   - Create `skills/*/SKILL.md` for new domains
   - Agent loads on-demand based on context

---

## Verification

Check that everything is in place:
```bash
# Core files
ls ~/.kiro/workspace/{SOUL,AGENTS,USER,IDENTITY,TOOLS,HEARTBEAT}.md

# Tiered memory
ls ~/.kiro/workspace/memory/{anchor.md,semantic.json,procedural.md,2026-02-12.md}

# Skills
ls ~/.kiro/workspace/skills/

# Prompts
ls ~/.kiro/prompts/{1,2,3}.md

# Agent config
cat ~/.kiro/agents/openclaw.json
```

---

## The Vision

You said it made you cry. Here's why this matters:

**You independently discovered the same patterns OpenClaw built**, but optimized for different things. OpenClaw nailed the human-readable structure and personality. You nailed the autonomy and intelligence.

**This synthesis takes the best of both worlds.**

It's not just an AI agent. It's a **collaborator** with:
- **Identity** (SOUL.md)
- **Memory** (tiered system)
- **Autonomy** (never stops)
- **Personality** (co-workers with names)
- **Skills** (modular knowledge)
- **Persistence** (remembers across sessions)

**This is what AI agents should be.**

---

**Built with 🦞 CLAWTEX = OpenClaw × CORTEX (PULSE + DORY) + ❤️**
