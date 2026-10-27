# Oliver Yu

I work on LLM inference, mostly on Apple silicon with MLX, Core ML and the Neural Engine. A lot
of that is measuring runtimes: how well the cache gets reused, what happens under concurrency,
whether the same request gives the same output, where the latency actually goes. When I find a
bug in something I depend on, I send the fix upstream — including to MLX, oMLX, ROCm AITER,
vLLM and Apple's coremltools.

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
- **Merged** · [#4035](https://github.com/jundot/omlx/pull/4035 "fix(scheduler): clear SpecPrefill state after failures and cache rejects"): After a failed SpecPrefill request, stale state could hang the engine or make the retry prefill the wrong tokens.

**ROCm AITER**

- **Merged** · [#6693](https://github.com/ROCm/aiter/pull/6693 "[Config] Qwen3.8-Flash-Next FP8 fused-MoE tuned configs for gfx942 (MI325X, 304 CUs)"): Qwen3.8-Flash-Next FP8 fused MoE had no tuned rows for MI325X (gfx942, 304 CUs) and ran the default configs. The patch adds eight tuned rows: 3.7–13% less fused-MoE time on those shapes in the tuner's compare report. End to end, cold prefill moved +0.8%; decode mostly doesn't hit the new rows.

**vLLM**

- Open · [#62589](https://github.com/vllm-project/vllm/pull/62589 "[ROCm][Perf][Qwen4Exp] Tile QSA indexer scoring and skip invisible columns"): The ROCm sparse-attention indexer scored every row against the full page-table width; in a 32K prefill on MI325X that kernel took 43% of GPU time. The patch skips columns past each request's visible range and tiles the scoring. An independent tester measured 1.61× geometric-mean output throughput over 12 cases on MI355X, on the first revision.
<!-- OSS-SELECTED:END -->

<sub>Status syncs from GitHub daily. The rest:
[All upstream pull requests](#all-upstream-pull-requests).</sub>

## Projects

**[laya-apple](https://github.com/tc3oliver/laya-apple)**: runs
[Laya](https://github.com/NandhaKishorM/laya) on the MLX GPU and the Neural Engine
concurrently, with every output checked against upstream Laya. Profiling showed GPU tail latency climbing
whenever the Neural Engine ran; tracing it led to the coremltools patch above. laya-apple
uses Core ML's async API instead of waiting for the patch, and falls back to its earlier path if
it detects the slow state. Median GPU result return on an M4 Max went from 4–9 ms to about
0.04 ms, with no mismatches across 154 validation runs.
[Research notes](https://github.com/tc3oliver/laya-apple/blob/main/research/README.md) ·
[PyPI](https://pypi.org/project/laya-apple/)

**[llm-inference-systems](https://github.com/tc3oliver/llm-inference-systems)**: experiments on
what inference optimizations cost later requests: a sparse prefill that stops the reusable prefix
growing, speculative decoding where verify cost matters more than acceptance rate, and rebuilding
the reusable state in the background. The oMLX maintainer closed my pull request (#3964) without
merging, arguing recovery at best matches SpecPrefill off; I never ran a clean off to compare against.
[Case study](https://meowcoder.com/work/llm-inference-systems/) ·
[Engineering notes](https://github.com/tc3oliver/llm-inference-systems/blob/main/ENGINEERING.md)

**[Embed2ASR](https://github.com/tc3oliver/embed2asr)**: a small reader trained on a frozen
EmbeddingGemma 2 audio encoder transcribes Mandarin, English and code-switched speech. On one MI300X it ran 4.16× faster than Whisper large-v3,
which wins on most test sets.
[Case study](https://meowcoder.com/work/embed2asr/) ·
[Write-up](https://study.meowcoder.com/posts/261016-embed2asr-frozen-encoder/)

**[qwen3.8-27b-5070ti-eval](https://github.com/tc3oliver/qwen3.8-27b-5070ti-eval)**: a
pre-registered evaluation of a 27B model on one 16 GB RTX 5070 Ti, with raw data and graders. It
scores 92.1 % on HumanEval+. The first competitor spilled out of VRAM mid-run, so I voided that
run and round 1 makes no comparison. Under WSL2 a 128K context loaded without an error but
decoded at 5.9 tok/s, apparently because some memory had landed in system RAM.
[Article](https://study.meowcoder.com/posts/261003-qwen38-27b-5070ti-round1/) ·
[Evidence index](https://github.com/tc3oliver/qwen3.8-27b-5070ti-eval/blob/main/EVIDENCE-INDEX.md)

**[PiShip](https://github.com/tc3oliver/piship)**: lets a company ship
[Pi](https://github.com/earendil-works/pi) as its own coding agent without forking it. Pi keeps
the agent loop and tools; PiShip adds OIDC login, short-lived credentials for an internal LLM
gateway, policy, MCP rules and a sandbox. If a required sandbox can't start, the command doesn't
run. Pre-release; every release archive is attested and built twice to check that the
payloads match. TypeScript.
[Status](https://github.com/tc3oliver/piship/blob/main/docs/status.md) ·
[Enterprise integration](https://github.com/tc3oliver/piship/blob/main/docs/enterprise-integration.md)

Smaller things: [SignalForge](https://github.com/tc3oliver/signalforge), a self-hosted
intelligence pipeline; [version-aware-code-mcp](https://github.com/tc3oliver/version-aware-code-mcp),
an MCP server that keeps a coding agent's code search on the right commit;
[deepseek-v4-flash-mi300x](https://github.com/tc3oliver/deepseek-v4-flash-mi300x), a vLLM serving
baseline on AMD MI300X;
[claude-team-kit](https://github.com/tc3oliver/claude-team-kit), a Claude Code plugin that limits
concurrent agent-team workers and shows them in a Mission Control pane
(pre-release); [Shouri](https://shouri.app);
[my coding-agent skills](https://github.com/tc3oliver/skills).

## Writing

I write up research at [study.meowcoder.com](https://study.meowcoder.com), in Traditional
Chinese. Two good places to start:
[當 prefill 變快，agent 反而變慢](https://study.meowcoder.com/posts/260920-inference-reusable-state/)
and [償還 reusable state 的債](https://study.meowcoder.com/posts/260921-canonical-state-debt-recovery/).

## All upstream pull requests

<!-- OSS-AUTO:START -->
49 pull requests to projects I don't maintain: 25 merged · 24 open.

**Apple coremltools** (1 open)

- ○ [#2876](https://github.com/apple/coremltools/pull/2876) Release the GIL during native MLModel prediction

**MLX** (1 merged)

- ✓ [#4615](https://github.com/ml-explore/mlx/pull/4615) Fix lost rank output in the distributed launcher

**oMLX** (7 merged · 6 open)

- ✓ [#4822](https://github.com/jundot/omlx/pull/4822) fix(unlimited-ocr): don't add a second &lt;image&gt; to a prompt that has one
- ✓ [#4035](https://github.com/jundot/omlx/pull/4035) fix(scheduler): clear SpecPrefill state after failures and cache rejects
- ✓ [#3685](https://github.com/jundot/omlx/pull/3685) fix(attention): keep SDPA256 prefill on the bounded route
- ✓ [#3842](https://github.com/jundot/omlx/pull/3842) feat(specprefill): preserve draft recurrent state at cache boundaries
- ✓ [#3840](https://github.com/jundot/omlx/pull/3840) fix(specprefill): derive draft cache position from attention layers
- ✓ [#3746](https://github.com/jundot/omlx/pull/3746) fix(ane): avoid impossible sequence-length guidance below the ANE minimum
- ✓ [#3664](https://github.com/jundot/omlx/pull/3664) fix(responses): route namespace tool groups through to the model and back
- ○ [#4500](https://github.com/jundot/omlx/pull/4500) perf(mtp): let greedy chains draft through the coarse lm\_head (opt-in)
- ○ [#4461](https://github.com/jundot/omlx/pull/4461) fix(specprefill): keep manual\_rope output in the input dtype
- ○ [#3962](https://github.com/jundot/omlx/pull/3962) test: reset the image decode cache between tests
- ○ [#3811](https://github.com/jundot/omlx/pull/3811) fix(specprefill): keep selected tokens at their original positions on mRoPE VLMs
- ○ [#3762](https://github.com/jundot/omlx/pull/3762) feat(anthropic): accept per-request SpecPrefill overrides on /v1/messages
- ○ [#3756](https://github.com/jundot/omlx/pull/3756) fix(specprefill): preserve the full static system/tool prefix

**Other projects** (17 merged · 17 open)

- ✓ [recursive-oss/rec#27](https://github.com/recursive-oss/rec/pull/27) Raise the HTTP server's listen backlog to 32
- ✓ [elie222/rakazo#2232](https://github.com/elie222/rakazo/pull/2232) fix(routines): refuse duplicate and excess routines in schedule\_create
- ✓ [elie222/rakazo#2101](https://github.com/elie222/rakazo/pull/2101) fix(mcp): honour the private-endpoint opt-in during OAuth
- ✓ [elie222/rakazo#2190](https://github.com/elie222/rakazo/pull/2190) fix(runtime): skip the SDK retry when a backup model is set
- ✓ [elie222/rakazo#2181](https://github.com/elie222/rakazo/pull/2181) fix(runs): deny an expired run's open approval
- ✓ [elie222/rakazo#2171](https://github.com/elie222/rakazo/pull/2171) fix(runs): deny an open approval when its run is stopped
- ✓ [elie222/rakazo#2167](https://github.com/elie222/rakazo/pull/2167) docs(self-host): restore a production snapshot into a new stack
- ✓ [elie222/rakazo#2168](https://github.com/elie222/rakazo/pull/2168) test(adapters): cover backup-model switching and the sub-agent tool-call fuse
- ✓ [elie222/rakazo#2149](https://github.com/elie222/rakazo/pull/2149) fix(approvals): replace the opposite rule when one is set
- ✓ [elie222/rakazo#2102](https://github.com/elie222/rakazo/pull/2102) fix(computer): resolve a leading \~ in file tool paths to the computer's home
- ✓ [elie222/rakazo#2103](https://github.com/elie222/rakazo/pull/2103) fix(routines): don't charge tool discovery against a watched tool's timeout
- ✓ [api7/aisix#1348](https://github.com/api7/aisix/pull/1348) refactor(bedrock): send Converse request bodies with a stable key order
- ✓ [ROCm/aiter#6693](https://github.com/ROCm/aiter/pull/6693) \[Config\] Qwen3.8-Flash-Next FP8 fused-MoE tuned configs for gfx942 (MI325X, 304 CUs)
- ✓ [NandhaKishorM/laya#260](https://github.com/NandhaKishorM/laya/pull/260) docs: add laya-apple to Community Tools
- ✓ [eiei114/pi-model-fallback#64](https://github.com/eiei114/pi-model-fallback/pull/64) fix(error-status): parse "Error: &lt;status&gt;" with no colon after the status
- ✓ [DrJuChunKoO/TransPal-gemini-transcriber#1](https://github.com/DrJuChunKoO/TransPal-gemini-transcriber/pull/1) feat: add resume-from-interruption support for long audio transcriptions
- ✓ [Baseflow/screenrecorder#9](https://github.com/Baseflow/screenrecorder/pull/9) fix: fix the black background
- ○ [vllm-project/vllm#63746](https://github.com/vllm-project/vllm/pull/63746) \[Perf\]\[Attention\] Larger prefill Q tile for Triton unified attention on sm80/sm89
- ○ [elie222/rakazo#2234](https://github.com/elie222/rakazo/pull/2234) fix(bot-messages): don't relay a bare NO\_RESPONSE to the asking bot
- ○ [elie222/rakazo#2231](https://github.com/elie222/rakazo/pull/2231) docs(self-host): restricted egress on Docker-in-VM hosts (OrbStack)
- ○ [elie222/rakazo#2230](https://github.com/elie222/rakazo/pull/2230) fix(web): let web\_fetch read past a truncated page
- ○ [Blaizzy/mlx-vlm#2596](https://github.com/Blaizzy/mlx-vlm/pull/2596) Compile Flint expert routing
- ○ [elie222/rakazo#2119](https://github.com/elie222/rakazo/pull/2119) fix(approvals): refuse a retry of an action the user denied in the same run
- ○ [ml-explore/mlx-lm#2006](https://github.com/ml-explore/mlx-lm/pull/2006) Skip fully masked key tiles in Flint sliding-window prefill
- ○ [recursive-oss/rec#25](https://github.com/recursive-oss/rec/pull/25) Use the causal mask mode for global-layer prefill attention
- ○ [recursive-oss/rec#23](https://github.com/recursive-oss/rec/pull/23) Share one sort between top\_p and top\_k sampling
- ○ [recursive-oss/rec#22](https://github.com/recursive-oss/rec/pull/22) Resolve each KV address once per token in long-context attention
- ○ [recursive-oss/rec#21](https://github.com/recursive-oss/rec/pull/21) Skip fully masked key tiles in sliding-window prefill attention
- ○ [BerriAI/litellm#47484](https://github.com/BerriAI/litellm/pull/47484) fix(least-busy): reserve the picked deployment so a burst of requests spreads out
- ○ [BerriAI/litellm#47483](https://github.com/BerriAI/litellm/pull/47483) fix(http\_handler): keep the connect timeout bounded when a request passes a numeric timeout
- ○ [vllm-project/vllm#62590](https://github.com/vllm-project/vllm/pull/62590) \[ROCm\]\[Perf\]\[Qwen4Exp\] Use BLOCK\_N=32 for sparse GQA prefill on gfx942
- ○ [vllm-project/vllm#62589](https://github.com/vllm-project/vllm/pull/62589) \[ROCm\]\[Perf\]\[Qwen4Exp\] Tile QSA indexer scoring and skip invisible columns
- ○ [ROCm/aiter#6692](https://github.com/ROCm/aiter/pull/6692) \[CK\] \[Bugfix\] FMoE tuner: use all sources for shapes FlyDSL v2 cannot tune
- ○ [ray-project/llmperf#100](https://github.com/ray-project/llmperf/pull/100) feat: Support reasoning\_content in OpenAI chat completions streaming response

<details>
<summary>Superseded, not counted</summary>

- [jundot/omlx#3793](https://github.com/jundot/omlx/pull/3793) feat(specprefill): recover reusable prefix state during idle time, replaced by [#3964](https://github.com/jundot/omlx/pull/3964), [#3962](https://github.com/jundot/omlx/pull/3962)

</details>
<!-- OSS-AUTO:END -->
