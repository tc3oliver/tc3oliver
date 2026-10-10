# Oliver Yu

I work on LLM inference, mostly on Apple silicon with MLX, Core ML and the Neural Engine. A lot
of that is measuring runtimes: how well the cache gets reused, what happens under concurrency,
whether the same request gives the same output, where the latency actually goes. When I find a
bug in something I depend on, I send the fix upstream — including to MLX, oMLX,
and Apple's coremltools.

[meowcoder.com](https://meowcoder.com) · [Research notes](https://study.meowcoder.com) ·
[tc3oliver@gmail.com](mailto:tc3oliver@gmail.com)

## Upstream contributions

<!-- OSS-SELECTED:START -->
**Apple coremltools**

- Open · [#2876](https://github.com/apple/coremltools/pull/2876 "Release the GIL during native MLModel prediction"): `MLModel.predict()` held the GIL for the whole native Core ML call, so other Python threads in the process stalled behind it. The patch releases it around the native call, with a threading test.

**MLX**

- **Merged** · [#4615](https://github.com/ml-explore/mlx/pull/4615 "Fix lost rank output in the distributed launcher"): The distributed launcher could lose a rank's final output when the process exited before its pipes were drained. The fix reads both pipes to EOF without blocking.

**oMLX**

- **Merged** · [#3685](https://github.com/jundot/omlx/pull/3685 "fix(attention): keep SDPA256 prefill on the bounded route"): The SDPA256 prefill path was picked by how much memory happened to be free, so the same request could give different temperature-0 output in two processes. Now the choice depends only on the input shape.
- **Merged** · [#3840](https://github.com/jundot/omlx/pull/3840 "fix(specprefill): derive draft cache position from attention layers") + [#3842](https://github.com/jundot/omlx/pull/3842 "feat(specprefill): preserve draft recurrent state at cache boundaries"): On hybrid attention/recurrent models the SpecPrefill draft cache never hit: a restored cache looked empty, and recurrent state wasn't saved at block boundaries.
- **Merged** · [#3664](https://github.com/jundot/omlx/pull/3664 "fix(responses): route namespace tool groups through to the model and back"): The Responses API dropped `namespace` tool groups, which is how Codex passes MCP tools, so the model never saw them.
- Open · [#3964](https://github.com/jundot/omlx/pull/3964 "feat(specprefill): recover reusable prefix state during idle time"): After a sparse prefill there is no reusable prefix, so a long append-only session keeps re-prefilling more and more. This rebuilds that state while the server is idle.
<!-- OSS-SELECTED:END -->

<sub>Status is synced from GitHub every week. Everything else is in
[All upstream pull requests](#all-upstream-pull-requests).</sub>

## Projects

**[laya-apple](https://github.com/tc3oliver/laya-apple)**: runs
[Laya](https://github.com/NandhaKishorM/laya) on the MLX GPU and the Neural Engine at the same
time, with every output checked against upstream Laya. While profiling it I saw GPU tail latency
climb whenever the Neural Engine was busy. The cause was Core ML's synchronous `predict` holding
the GIL, and that became the coremltools patch above. v1.5 doesn't wait for the patch to land: it
uses Core ML's async API, and if it detects the slow state it falls back to the 1.4 path. On an
M4 Max, median GPU result return dropped from 4–9 ms to about 0.04 ms, with no mismatches across
154 validation runs.
[Research notes](https://github.com/tc3oliver/laya-apple/blob/main/research/README.md) ·
[PyPI](https://pypi.org/project/laya-apple/)

**[llm-inference-systems](https://github.com/tc3oliver/llm-inference-systems)**: experiments on
what an inference optimization costs the requests after it. Three so far, each with its data and
plots: a sparse prefill that stops the reusable prefix from growing, speculative decoding where
verify cost decides whether it pays off more than acceptance rate does, and rebuilding the
reusable state in the background. The SpecPrefill PRs above came out of this work.
[Case study](https://meowcoder.com/work/llm-inference-systems/) ·
[Engineering notes](https://github.com/tc3oliver/llm-inference-systems/blob/main/ENGINEERING.md)

**[qwen3.8-27b-5070ti-eval](https://github.com/tc3oliver/qwen3.8-27b-5070ti-eval)**: a
pre-registered evaluation of a 27B model on one 16 GB RTX 5070 Ti, with raw data and graders. It
scores 92.1 % on HumanEval+. The first competitor spilled out of VRAM mid-run, so I voided that
run and round 1 makes no comparison. Under WSL2 a 128K context loaded without an error, then
decoded a test request at 5.9 tok/s: some of the memory had apparently landed in system RAM,
without a warning.
[Article](https://study.meowcoder.com/posts/261003-qwen38-27b-5070ti-round1/) ·
[Evidence index](https://github.com/tc3oliver/qwen3.8-27b-5070ti-eval/blob/main/EVIDENCE-INDEX.md)

**[PiShip](https://github.com/tc3oliver/piship)**: lets a company ship
[Pi](https://github.com/earendil-works/pi) as its own coding agent without forking it. Pi keeps
the agent loop and tools; PiShip adds OIDC login, short-lived credentials for an internal LLM
gateway, policy, MCP rules and a sandbox. If a required sandbox can't start, the command doesn't
run. Pre-release. Every archive in a release is attested and built twice to check that the
payloads match, and the status page lists what is not verified yet. TypeScript.
[Status](https://github.com/tc3oliver/piship/blob/main/docs/status.md) ·
[Enterprise integration](https://github.com/tc3oliver/piship/blob/main/docs/enterprise-integration.md)

Smaller things: [SignalForge](https://github.com/tc3oliver/signalforge), a self-hosted
intelligence pipeline; [version-aware-code-mcp](https://github.com/tc3oliver/version-aware-code-mcp),
an MCP server that keeps a coding agent's code search on the right commit;
[deepseek-v4-flash-mi300x](https://github.com/tc3oliver/deepseek-v4-flash-mi300x), a vLLM serving
baseline on AMD MI300X;
[claude-team-kit](https://github.com/tc3oliver/claude-team-kit), a Claude Code plugin that caps
how many agent-team workers run at once and shows them live in a Mission Control pane
(pre-release); [Shouri](https://shouri.app);
[my coding-agent skills](https://github.com/tc3oliver/skills).

## Writing

I write up research at [study.meowcoder.com](https://study.meowcoder.com), in Traditional
Chinese. Two good places to start:
[當 prefill 變快，agent 反而變慢](https://study.meowcoder.com/posts/260920-inference-reusable-state/)
and [償還 reusable state 的債](https://study.meowcoder.com/posts/260921-canonical-state-debt-recovery/).

## All upstream pull requests

<!-- OSS-AUTO:START -->
20 pull requests to projects I don't maintain: 11 merged · 9 open.

**Apple coremltools** (1 open)

- ○ [#2876](https://github.com/apple/coremltools/pull/2876) Release the GIL during native MLModel prediction

**MLX** (1 merged)

- ✓ [#4615](https://github.com/ml-explore/mlx/pull/4615) Fix lost rank output in the distributed launcher

**oMLX** (6 merged · 7 open)

- ✓ [#4035](https://github.com/jundot/omlx/pull/4035) fix(scheduler): clear SpecPrefill state after failures and cache rejects
- ✓ [#3685](https://github.com/jundot/omlx/pull/3685) fix(attention): keep SDPA256 prefill on the bounded route
- ✓ [#3842](https://github.com/jundot/omlx/pull/3842) feat(specprefill): preserve draft recurrent state at cache boundaries
- ✓ [#3840](https://github.com/jundot/omlx/pull/3840) fix(specprefill): derive draft cache position from attention layers
- ✓ [#3746](https://github.com/jundot/omlx/pull/3746) fix(ane): avoid impossible sequence-length guidance below the ANE minimum
- ✓ [#3664](https://github.com/jundot/omlx/pull/3664) fix(responses): route namespace tool groups through to the model and back
- ○ [#4215](https://github.com/jundot/omlx/pull/4215) fix(mtp): keep greedy Qwen3.5 verify independent of the draft depth
- ○ [#3964](https://github.com/jundot/omlx/pull/3964) feat(specprefill): recover reusable prefix state during idle time
- ○ [#3962](https://github.com/jundot/omlx/pull/3962) test: reset the image decode cache between tests
- ○ [#3811](https://github.com/jundot/omlx/pull/3811) fix(specprefill): keep selected tokens at their original positions on mRoPE VLMs
- ○ [#3792](https://github.com/jundot/omlx/pull/3792) docs(scheduler): fix the SpecPrefill note in the prefill-OOM requeue path
- ○ [#3762](https://github.com/jundot/omlx/pull/3762) feat(anthropic): accept per-request SpecPrefill overrides on /v1/messages
- ○ [#3756](https://github.com/jundot/omlx/pull/3756) fix(specprefill): preserve the full static system/tool prefix

**Other projects** (4 merged · 1 open)

- ✓ [NandhaKishorM/laya#260](https://github.com/NandhaKishorM/laya/pull/260) docs: add laya-apple to Community Tools
- ✓ [eiei114/pi-model-fallback#64](https://github.com/eiei114/pi-model-fallback/pull/64) fix(error-status): parse "Error: &lt;status&gt;" with no colon after the status
- ✓ [DrJuChunKoO/TransPal-gemini-transcriber#1](https://github.com/DrJuChunKoO/TransPal-gemini-transcriber/pull/1) feat: add resume-from-interruption support for long audio transcriptions
- ✓ [Baseflow/screenrecorder#9](https://github.com/Baseflow/screenrecorder/pull/9) fix: fix the black background
- ○ [ray-project/llmperf#100](https://github.com/ray-project/llmperf/pull/100) feat: Support reasoning\_content in OpenAI chat completions streaming response

<details>
<summary>Superseded, not counted</summary>

- [jundot/omlx#3793](https://github.com/jundot/omlx/pull/3793) feat(specprefill): recover reusable prefix state during idle time, replaced by [#3964](https://github.com/jundot/omlx/pull/3964), [#3962](https://github.com/jundot/omlx/pull/3962)

</details>
<!-- OSS-AUTO:END -->
