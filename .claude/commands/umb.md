---
description: Update Memory Bank with current PCB development context
---

# Update Memory Bank (UMB)

Update the memory bank with current PCB development context and decisions.

**REQUIRED**: Use this command after any significant development work to maintain project context.

## Updates These Files:
- `.memory_bank/activeContext.md` - Current session state and focus areas
- `.memory_bank/decisionLog.md` - New architectural decisions and trade-offs  
- `.memory_bank/progress.md` - Milestone updates and development metrics
- `.memory_bank/productContext.md` - Project overview refinements

## When to Use:
- After implementing placement or routing features
- When making PCB API design decisions
- After completing manufacturing integration work
- Before switching development focus areas
- After resolving complex format compatibility issues

The memory bank enables AI assistants to maintain rich context about PCB manipulation development patterns and architectural decisions across sessions.