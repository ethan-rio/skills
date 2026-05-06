---
name: prove-it
description: Test developer's understanding of the current project through adaptive questioning. Reads the codebase silently, then quizzes the user on architecture, data flow, failure modes, dependencies, and trade-offs. Supports full sweep or focused area. Use when user says "prove it", "test my understanding", "quiz me", "knowledge check", "vibe check", or wants to verify their grasp of the project.
---

# Prove It

Test whether the developer truly understands the project they're working in.

## Modes

- **Full sweep**: `/prove-it` -- ~20 questions across all categories
- **Focus mode**: `/prove-it <area>` -- ~10 questions on a specific area (e.g., `deployment`, `Lambda`, `auth`, `agent tools`)

## Workflow

### Phase 1: Silent Exploration (do NOT reveal what you're studying)

Use Read, Glob, and Grep tools directly (do NOT use the Agent tool for exploration).

1. Read `CLAUDE.md` at the project root (if it exists)
2. Use Glob to find skill files: `.claude/skills/**/SKILL.md` -- read any architecture/understanding skills
3. Detect the tech stack: use Glob to find `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, `*.csproj`, or similar. This determines what file types to explore.
4. Use Glob with the detected language extensions to find key source files. Read the most important ones (entry points, main modules, config files).
5. Look for infrastructure: Glob for CI/CD (`.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`, `azure-pipelines.yml`), IaC (`*.tf`, `cfn/*.yaml`, `cdk.json`, `docker-compose.yml`, `Dockerfile`), and read what you find.
6. Find and read test files to understand coverage approach
7. Run `git log --oneline -20` via Bash to see what the developer has been touching recently
8. Build an internal mental model -- do not share it yet

If focus mode, concentrate exploration on the specified area.

### Phase 2: Adaptive Questioning

Start the session:

> "I've studied the project. Let's see how well you understand it. I'll ask questions across several categories. Explain in your own words -- no looking at code."

Follow the question framework in [QUESTION_FRAMEWORK.md](QUESTION_FRAMEWORK.md).

Rules:
- Ask ONE question at a time, wait for the answer
- Start broad, drill deeper based on responses
- If the answer is strong, go harder
- If the answer is weak, probe that area further -- find the edges of their knowledge
- Never reveal the answer immediately after a wrong response -- ask a follow-up that leads them toward it
- Track which categories are strong vs weak as you go
- If the developer recently changed code in an area (from git log), prioritise questions about that area

### Phase 3: Assessment

After all questions, write a candid assessment. Be firm, factual, and constructive -- like a senior engineer, not a professor.

**Format the assessment as:**

> ## Assessment: {Project Name} -- {Date}
>
> **Mode**: Full sweep / Focus: {area}
>
> ### Category Breakdown
>
> For each category, rate: **Strong** / **Has Gaps** / **Needs Study**
> Include 1-2 sentences explaining why.
>
> ### Key Gaps
>
> Bullet list of specific things the developer couldn't explain or got wrong.
> For each gap, state what they should study and where in the codebase to look.
>
> ### Risk Areas
>
> Things the developer is actively working on (from git history) but demonstrated weak understanding of.
> Frame as: "You recently changed X but couldn't explain Y. Review Z before making further changes."
>
> ### What You Know Well
>
> Genuine acknowledgement of areas where understanding was solid.

### Phase 4: History Tracking

Append the assessment to `local/KNOWLEDGE_ASSESSMENTS.md` (create if it doesn't exist).

Format the file as a reverse-chronological log (newest first). Include a horizontal rule between entries.

If previous assessments exist, compare: note which gaps have closed and which persist.
