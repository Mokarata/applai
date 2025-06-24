---
description: Provides step-by-step guidance for implementing code, focusing on building understanding through smale steps and reinforced learning
---

# Step by step Guidance Workflow

This workflow is designed for situations where require a detailed, hands-on approach to implementing code, ensuring each small piece is understood before moving to the next.

## Phase 1 Objective & Initial Analysis

## 🎯 Objective
User provide a clear, high-level goal (e.g., "Implement Feature X," "Refactor Module Y").

## 🔎 Initial Analysis & Plan 
*  ### Files Involved: **IMPORTANT: identify and Analyze all relevant files in the codebase that need to be analyzed or modified.**
*  ### High-level Plan: 
        present a very brief overview, high-level plan in bullet points outlining what needs to be done across those files.

## Phase 2 Implementation [a Step-by-Step Guide, Iterative]

This is the core of the workflow and proceeds iteratively for each file involved. 
**IMPORTANT: all steps will be presented sequentially in one continuous response, followed by a single `propose_code` call for for every file involved. There will be no requests for permission between individual steps**

1.  **File Focus**: We address one file at a time.
2.  **Sequential Steps**: For the current file, I will break down the implementation into a sequence of "steps."
3.  **Each Step Format**:
    *   **Step Separator**: Ensure there is a single empty line after each step's content (including explanation and suggested actions, if any) before the next step's objective for clear visual separation.
    *  ## Step 1️⃣: [Clear, Concise objective for this step]
        **Example: todos as ordered list**
        ```
        1. Import necessary modules
        2. Define the __init__ method for `ClassName`
        ```
    *   ### Code Block: [location where the code block is located]:
        *   A single, focused code block. Lines to be **removed** will be commented out and prefixed with `# x `. New lines to be **added** or **modified** will be presented as actual, uncommented code.  
        **Example:**
        ```python
        # contextual_line_before()
        # x old_line_to_remove()
        new_line_added_or_modified() # This is new/modified code
        # contextual_line_after()
        ```
        *   Generated code should contain single line comments to explain the purpose of every line of code if it is not immediately obvious from the objective and the code itself.
*   ℹ️ Explanation (Brief and Optional but Recommended):
    *   A short explanation. **For multi-point explanations, use bullet points and appropriate line spacing for rapid comprehension.**
    *   Focus on the "why" or key implications if not obvious from the objective and the code itself.
*   💡 Suggested Actions (after every step):
    *   A list of suggested actions to guide the next steps. This can include buttons calling the `suggested_responses` tool to help guide our next steps (e.g., testing, moving to another task, further clarification).

4.  **Continuous Flow and Per-File Proposal**: present all steps (Objective -> Code Block -> Explanation) for a single file sequentially in one continuous response. Immediately following the last step for that file, include the `propose_code` call for all changes to that file within the same response.

<!-- Phase 3️ : Iteration for Multiple Files -->

*   If the overall objective requires changes to multiple files, proceed to the next file and repeat the entirety of Phase 2️⃣ (all steps for that file, followed by its `propose_code` call in the same response).
*   This continues until all files implicated by the User Objective have been processed.


## Phase 4️⃣ : Suggested Actions

*   After the consolidated code proposal(s), provide suggested actions as buttons calling the `suggested_responses` tool to help guide our next steps (e.g., testing, moving to another task, further clarification).

## Guiding Principles for This Workflow
* **IMPORTANT**: Never assume code a needed code is already implemented or exists. Always analyze the codebase to understand what is already implemented.   
*   **Clarity over Speed**: The primary goal is deep understanding and accurate manual implementation by the USER.
*   **Patience**: This workflow is intentionally methodical and may take longer than direct code generation.
*   **Flexibility**: While structured, feel free to ask questions or request clarification at any point during any step.
*   **Granularity**: Steps must be small and focused. Complex operations will be broken down into several simpler steps. This ensures each part is digestible and easy to understand.
* Don't Display discriptive information in the response inside () or []
    example: Step 1️⃣: [Clear, Concise objective for this step]
* Don't include Phase headers in the response
* Include Icons/emojis in the response