# Dojo: The Coding Agent Built to Finish

Coding with AI should feel less like supervising an autocomplete engine and more like working beside an experienced engineer.

That means understanding the system before changing it. Tracing a bug across boundaries instead of patching the first suspicious line. Explaining the design clearly. Making focused edits. Running the checks. Reviewing the actual diff. And staying with the work until the result meets a real Definition of Done.

That is the coding experience Dojo was built to deliver.

Dojo can read a codebase, search it broadly, edit it precisely, run its tools, inspect failures, use a browser when the bug lives in the interface, and verify the result. More importantly, it coordinates those abilities as one working process. The goal is not to produce the most text or summon the most agents. The goal is to reach a correct, reviewable result with less waste.

## Understand the design before touching the code

A difficult bug rarely lives inside one isolated function.

The symptom may appear in the interface while the cause sits in state management. A request may fail at the API boundary because a type changed three layers earlier. A race condition may only become visible when two otherwise-correct operations overlap.

Dojo begins by building a working model of the system: where data enters, how it moves, what owns each decision, and where the observed behavior diverges from the intended behavior. It searches call sites, follows types, reads tests, checks configuration, and narrows the investigation before making changes.

That internal understanding matters because fast edits are not the same as fast engineering. The quickest patch can become tomorrow’s second bug.

When the design is easier to see than to describe, Dojo can turn it into a flowchart, state machine, sequence diagram, dependency graph, or architecture map. These are not decorative pictures. They create a shared model between the developer and the agent.

A flowchart can expose a missing branch. A state machine can reveal an impossible transition. A sequence diagram can show who is waiting on whom. A dependency graph can make an unexpected coupling obvious.

Instead of asking you to absorb another wall of prose, Dojo can show the shape of the system and ask: **is this the design you intended?**

That shortens the distance between investigation and agreement.

## Debugging is an evidence problem

Dojo treats debugging as a sequence of testable claims.

First, reproduce the failure or identify the strongest observable evidence. Then trace the path that produces it. Form a hypothesis. Test the hypothesis with the smallest useful check. Make the narrowest coherent correction. Finally, run the validation that would disprove the fix if it were wrong.

The tools change with the bug. A compiler error needs a compile. A runtime regression needs logs or a reproducible path. A visual defect needs the actual rendered interface at the affected viewport. A network problem needs request and response evidence. A concurrency problem needs attention to ordering, shared state, and timing.

Dojo can move through those layers without turning the conversation into a paste bin. Reads, searches, test output, screenshots, and diffs are presented as the artifacts they are. The explanation stays focused on what changed in the diagnosis.

That distinction keeps the interface clean while preserving the evidence a developer needs.

## One Maestro, purpose-sized specialists

Dojo’s primary coding partner is the Maestro: the agent that owns the conversation, the plan, the edits, and the final result.

When the work benefits from parallel investigation or an independent perspective, the Maestro can bring in purpose-sized specialists:

- **Prime** for deep, multi-angle reasoning or adversarial review.
- **General** for contained implementation and debugging work that requires judgment.
- **Utility** for fast, deterministic searches, checks, and mechanical work.

The names matter less than the discipline behind them. A small lookup should not consume the same reasoning budget as an architectural investigation. A task that needs judgment should not be handed to a lightweight worker merely because it is cheaper. Work should be routed to the smallest capable agent, with a clear scope and a clear finish line.

This is how Dojo is designed to do more with less: not by starving the work, but by spending attention where attention changes the outcome.

A second Maestro can also join through Lane Assist when a different perspective is genuinely useful. That is especially valuable for independent review, testing, or challenging an assumption. It is a supporting capability here; code review and Lane Assist deserve their own deeper treatment.

## The interface is built for engineering, not transcript archaeology

A coding agent should not make developers excavate the answer from a scrolling monologue.

Dojo keeps source reads, syntax-highlighted code, tool activity, diagrams, and diffs in dedicated visual surfaces. Agent work can remain compact and expandable. The conversation explains the decision; the artifact carries the exact detail.

Diff review supports both common reading styles:

- **Side by side** when you want to compare old and new lines directly.
- **Top to bottom** when a unified narrative is easier to follow.

Added, removed, and unchanged lines retain their line numbers and structure. You can inspect what actually changed rather than trusting a summary that says everything is fine.

The same principle applies to design communication. A state machine belongs in a state-machine view. A graph belongs in a graph. Source belongs in a source viewer. The interface should match the shape of the information.

## Talk through the bug without losing the code

Coding is visual work. Your eyes are already tracking source, output, diagrams, and the running product.

Dojo lets you talk through a problem while keeping your attention on those artifacts. Explain the symptom naturally. Add the detail you remembered halfway through. Interrupt when the investigation goes in the wrong direction. Ask for the short version, the deeper explanation, or a visual model.

Dojo can speak back in the same working rhythm.

Voice does not replace exact text. Code, commands, file names, and diffs still need precision. Voice removes the requirement that every thought begin as a perfectly formatted prompt, and it lets the explanation continue while your eyes remain on the work.

The result is a tighter debugging loop without turning the developer into a full-time transcript reader.

## Done means the Definition of Done is satisfied

Some products describe repeated agent attempts as a “loop.” Software teams already have a clearer industry term: the **Definition of Done**.

The job is not complete because the agent stopped or because one test passed. It is complete when the agreed evidence says the work is complete: the failure is resolved, required checks pass, the diff is coherent, and the requested behavior is present.

When Dojo believes that finish line has been reached, an independent auditor—potentially powered by a different model—can challenge the claim against the stated Definition of Done. The auditor’s role is not to congratulate the main agent. It is to keep it honest.

That is only a touch of the idea. Definition of Done deserves a post of its own.

## Historical benchmarks: faster where orchestration matters

Performance claims should come with context. The following repository-recorded benchmarks were run in March 2026. They are historical, single-run system comparisons on specific coding audits—not universal claims about every model, repository, or task.

| Historical audit | Dojo | Comparison harness | Time | Token result | Reviewed outcome |
| --- | --- | --- | ---: | ---: | --- |
| Four-area code audit | Multi-agent Dojo | Claude Code | **63% faster** | **86% fewer effective tokens** | Both covered all four audit areas with zero reported errors |
| Coding audit | Multi-agent Dojo | Codex CLI | **73% faster** | Dojo used **97% more tokens** | Dojo produced the stronger manually reviewed answer; Codex was about 4.1× cheaper |

The Claude result demonstrates the efficiency Dojo’s orchestration can achieve when work divides cleanly across a serious audit. The Codex result shows a different trade-off: Dojo reached the reviewed result much faster and at higher judged quality, while Codex won decisively on token use and cost.

That second result belongs in the table because credible engineering does not hide the column it lost.

| What the figures mean | What they do not mean |
| --- | --- |
| Recorded outcomes for two specific March 2026 audits | A guarantee that every Dojo task is faster |
| End-to-end harness comparisons, not isolated model-speed tests | Proof that one underlying model is universally better |
| Manual review of answer quality in the recorded reports | A blinded, statistically significant benchmark suite |
| Evidence that orchestration can change speed, token use, and result quality | Permission to collapse every trade-off into one marketing percentage |

Dojo has continued to improve since those runs, but improvement should not be converted into a new percentage until a fresh benchmark measures it. The useful claim is simpler: Dojo is engineered to spend models, tools, context, and parallelism deliberately—and its historical results show why that architecture is worth measuring.

## Built to carry the work across the line

The best coding agent is not the one that writes the most code in the first minute.

It is the one that understands enough of the system to change the right thing. It makes the design visible when words become inefficient. It chooses the right amount of reasoning for each part of the job. It lets you inspect the real diff. It keeps you involved through natural conversation. It tests its assumptions. And it does not confuse stopping with finishing.

That is the promise behind coding with Dojo:

**Understand the system. Debug with evidence. Show the design. Make the change. Verify the result. Finish the job.**
