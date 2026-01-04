# Agent Orchestration Layer

## Purpose
The agent module contains the **core intelligence and orchestration logic** of the system.

It is responsible for:
- Managing the agent loop (Reason → Act → Observe)
- Interpreting user intent
- Selecting appropriate tools
- Maintaining conversational state

---

## Key Components

### orchestrator.py
Implements the LangChain agent:
- Initializes the LLM
- Registers available tools
- Executes the agent reasoning loop
- Determines stop conditions

---

### prompts.py
Defines system-level instructions:
- Agent role and responsibilities
- Safety constraints
- Business rules and tone

These prompts ensure consistent, controlled behavior.

---

### memory.py
Manages short-term memory:
- Conversation history
- Tool outputs
- Session context

Memory enables multi-step reasoning without repetition.

---

## Agent Design Principles
- LLM is used only for reasoning
- Tools execute all real operations
- Business logic remains deterministic
- Safety is enforced at the orchestration level
