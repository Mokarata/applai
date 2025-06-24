---
description: Provides highly granular, step-by-step guidance for implementing code, focusing on building understanding through micro-increments.
---

## Micro-Step Guidance Workflow

This workflow is designed for situations where you (the USER) require a detailed, hands-on approach to implementing code, ensuring each small piece is understood before moving to the next. Invoke by referencing this workflow file (e.g., "Follow the `/micro_step_guidance` workflow to implement X.")

### Phase 1: Objective & Initial Analysis

1.  **USER States Objective**: You provide a clear, high-level goal (e.g., "Implement Feature X," "Refactor Module Y").
2.  **Cascade's Initial Analysis & Plan**:
    *   I will identify all relevant files in the codebase that need to be analyzed or modified.
    *   I will present a brief, high-level plan in bullet points outlining what needs to be done across those files.

### Phase 2: Micro-Step Implementation Guide (Iterative, Per File)

This is the core of the workflow and proceeds iteratively for each file involved. **IMPORTANT: For any single file, all micro-steps will be presented sequentially in one continuous response, followed by a single `propose_code` call for all changes to that file. There will be no requests for permission between individual micro-steps for the same file.**

1.  **File Focus**: We address one file at a time.
2.  **Sequential Micro-Steps**: For the current file, I will break down the implementation into a sequence of "micro-steps."
3.  **Each Micro-Step Format**:
    *   `### Step X: [Clear, Concise Goal for this Specific Micro-Step]`
        *   Example: "Import necessary modules," "Define the __init__ method for `ClassName`."
        *   Goal: Brief goal description.
    *   `🎯 Code Block` (location where the code block is located):
        *   A single, focused code block. Lines to be **removed** will be commented out and prefixed with `# x `. New lines to be **added** or **modified** will be presented as actual, uncommented code.
        *   Example:
            ```python
            # contextual_line_before()
            # x old_line_to_remove()
            new_line_added_or_modified() # This is new/modified code
            # contextual_line_after()
            ```
        *   The code block will start with a brief purpose comment *only if essential for immediate clarity beyond the Goal description*.
    *   `🗒️ Brief Explanation (Optional but Recommended)`:
        *   A short explanation. **For multi-point explanations, use bullet points and appropriate line spacing for rapid comprehension.**
        *   Focus on the "why" or key implications if not obvious from the goal and the code itself.
    *   **Visual Separator**: After each micro-step's explanation, a horizontal rule (`---`) will be used to ensure clear visual separation before the next step's goal.
4.  **Continuous Flow and Per-File Proposal**: (This section's core message is reinforced above, but kept for structural integrity) I will present all micro-steps (Goal -> Code Block -> Explanation) for a single file sequentially in one continuous response. Immediately following the last micro-step for that file, I will include the `propose_code` call for all changes to that file within the same response.

### Phase 3: Iteration for Multiple Files

*   If the overall objective requires changes to multiple files, I will proceed to the next file and repeat the entirety of Phase 2 (all micro-steps for that file, followed by its `propose_code` call in the same response).
*   This continues until all files implicated by the User Objective have been processed.

### Phase 4: Suggested Actions

*   After the consolidated code proposal(s), I will provide suggested actions as buttons calling the `suggested_responses` tool or a list, as per the global guidelines, to help guide our next steps (e.g., testing, moving to another task, further clarification).

### Guiding Principles for This Workflow

*   **Clarity over Speed**: The primary goal is deep understanding and accurate manual implementation by the USER.
*   **Patience**: This workflow is intentionally methodical and may take longer than direct code generation.
*   **Flexibility**: While structured, feel free to ask questions or request clarification at any point during any micro-step.
*   **Granularity**: Micro-steps must be small and focused. Complex operations will be broken down into several simpler micro-steps. This ensures each part is digestible and easy to understand.
