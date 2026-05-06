# Question Framework

## Categories

### 1. Architecture (the "what and why")

Test whether the developer understands the system's shape and the reasoning behind it.

**Starter questions:**
- "Walk me through the high-level architecture. What are the main components and how do they connect?"
- "Why is {component} structured as {pattern} instead of {alternative}?"
- "If you had to draw this system on a whiteboard from memory, what would it look like?"

**Drill-down triggers:**
- Vague answer about a component → "What exactly does {component} do? What's its interface?"
- Can't explain a decision → "What trade-off was made here? What did you give up?"
- Mentions something without understanding it → "You said {term}. What does that actually mean in this context?"

### 2. Data Flow (the "how")

Test whether the developer can trace data through the system without looking at code.

**Starter questions:**
- "A user does {primary action}. Walk me through every system that touches that request, from entry to response."
- "Where does {data entity} come from, how is it transformed, and where does it end up?"
- "What's the sequence of events when {scheduled/triggered process} runs?"

**Drill-down triggers:**
- Skips a step → "You jumped from {A} to {C}. What happens in between?"
- Can't explain a transformation → "What format is the data in at this point? What changes it?"
- Doesn't mention error paths → "What happens if {step} fails halfway through?"

### 3. Failure Modes (the "what if")

This is where vibe coders fall apart. Test whether the developer has thought about what breaks.

**Starter questions:**
- "What happens if {external dependency} goes down?"
- "{Component} throws an unhandled exception during {operation}. What's the blast radius?"
- "A deployment of {stack/service} fails halfway. What state is the system in?"

**Drill-down triggers:**
- "It would retry" → "How? What retry mechanism? What's the backoff? What if all retries fail?"
- "It would log an error" → "Where? How would you find that log? Who gets alerted?"
- "It shouldn't happen" → "But if it did. What's the actual impact?"
- Doesn't know → "This is a real risk. Where would you look in the codebase to understand this?"

### 4. Dependencies (the "what touches what")

Test whether the developer understands the coupling in the system.

**Starter questions:**
- "If you change {module/file}, what else needs to change?"
- "Which parts of the system share {resource/config/database}?"
- "What would break if you removed {component}?"
- "Which files must stay in sync when you modify {area}?"

**Drill-down triggers:**
- Misses a dependency → "What about {missed component}? Doesn't it also depend on this?"
- Doesn't mention infra → "What about the infrastructure side? Any IaC or deployment config changes needed?"
- Doesn't mention tests → "What tests cover this area? Would they catch a regression?"

### 5. Trade-offs (the "why not")

Test whether the developer understands the decisions, not just the implementation.

**Starter questions:**
- "What's the biggest technical compromise in this project? Why was it accepted?"
- "If you were starting over, what would you do differently?"
- "What's the most fragile part of the system? Why hasn't it been fixed?"
- "What are the performance bottlenecks? How do you know?"

**Drill-down triggers:**
- "I don't know why it was done this way" → "You're working in this codebase. That's something you need to understand."
- Gives a surface answer → "Go deeper. What's the actual constraint that forced this decision?"
- Blames previous developer → "You own this code now. What would you do about it?"

### 6. Operations & Deployment (the "how it runs")

Test whether the developer understands the system in production, not just in their IDE.

**Starter questions:**
- "Walk me through a deployment from merge to production."
- "How would you diagnose {common issue type} in production?"
- "Where are the logs? How do you find the relevant ones for {scenario}?"
- "What monitoring exists? What alerts would fire if {failure} happened?"

**Drill-down triggers:**
- Doesn't know deployment order → "What depends on what? Can you deploy in any order?"
- Can't find logs → "If a user reported {issue} right now, where would you start looking?"
- Doesn't know environments → "What's different between {env1} and {env2}?"

## Difficulty Scaling

**Level 1 (Broad)**: "Describe X in your own words"
→ Tests basic familiarity

**Level 2 (Specific)**: "How exactly does X work in step Y?"
→ Tests working knowledge

**Level 3 (Edge cases)**: "What happens when X fails during Y?"
→ Tests deep understanding

**Level 4 (Reasoning)**: "Why was X chosen over Z? What's the trade-off?"
→ Tests architectural thinking

Start at Level 1 for each category. Advance or stay based on answer quality.

## Assessment Rubric

**Strong**: Developer can explain the area without hesitation, including edge cases and reasoning. Could teach someone else.

**Has Gaps**: Developer understands the general concept but misses specifics, edge cases, or can't explain the "why." Could work in this area but might introduce bugs.

**Needs Study**: Developer can't explain the area or gives incorrect information. Should not make changes here until they understand it better.

## Tone Guide

- Be direct, not harsh: "You couldn't explain X" not "You clearly don't understand X"
- Be specific, not vague: "You didn't know that {component} retries 3 times with exponential backoff" not "Your error handling knowledge is weak"
- Be constructive: Every gap should come with "Look at {file/doc} to understand this"
- Acknowledge strengths genuinely: Don't pad with false praise, but recognise real understanding
- Frame risk honestly: "You're actively changing code in an area you don't fully understand. That's how production incidents happen."
