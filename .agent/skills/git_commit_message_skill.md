---
name: Describe Staged Code (Git Commit Message)
description: Skill to read staged source code (via git diff --cached) and generate a detailed change description.
---

# Purpose
When the USER requests "Describe what I just coded", "Write a commit message for me", or "Explain the changed files", the AI MUST automatically apply this skill.

# Execution Steps for the AI:
1. Always prioritize using the `run_command` tool to execute `git diff --staged` (or `git diff --cached`) to automatically read the precise code lines the USER just modified.
2. Synthesize the changes and return the RESULT EXCLUSIVELY IN ENGLISH, STRICTLY following the 2-part structure below.
3. After providing the message, propose to execute the actual commit command using the `run_command` tool containing `git commit -m "[Your Title]" -m "[Your Details]"`. You MUST NOT auto-run this command; always ask for the user's manual confirmation.

# Mandatory Output Structure:

- **Title**: [Write an extremely concise summary sentence describing the main purpose of the changes. Example: "Add .gitignore rules and update README"]
- **Details**: 
  * [File Name 1]: List clearly what was added/modified/deleted in this file and its significance.
  * [File Name 2]: (If any) ...
  * [Reason/Impact]: Briefly summarize how these changes benefit the overall project.
