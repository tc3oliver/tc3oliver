# Oliver Yu

**LLM Systems / Inference Engineer**

Runtime · Serving · Prefill · Caching · Speculative Decoding · Heterogeneous Inference

I work on LLM inference runtimes and serving, mostly on Apple silicon with MLX, Core ML and the
Neural Engine: cache behavior, concurrency, correctness and measured performance. When a
measurement turns up a defect in a runtime I depend on, the fix goes upstream, so far to Apple
coremltools and oMLX.

[Portfolio](https://meowcoder.com) · [Research Notes](https://study.meowcoder.com) · [Email](mailto:tc3oliver@gmail.com)

## Selected OSS Contributions

<!-- OSS-SELECTED:START -->
**Apple coremltools**

- Open · [#2876](https://github.com/apple/coremltools/pull/2876 "Release the GIL during native MLModel prediction") — Synchronous `MLModel.predict()` holds the GIL for the entire native Core ML call, blocking other Python threads in the process that need it. Releases it around the native prediction only, with a threading regression test. Came out of the laya-apple GPU + ANE research.

**oMLX**

- **Merged** · [#3685](https://github.com/jundot/omlx/pull/3685 "fix(attention): keep SDPA256 prefill on the bounded route") — The SDPA256 prefill route was chosen from live memory headroom, so an identical request gave different temperature-0 output in different processes. The route now depends on the call shape alone.
- **Merged** · [#3840](https://github.com/jundot/omlx/pull/3840 "fix(specprefill): derive draft cache position from attention layers") + [#3842](https://github.com/jundot/omlx/pull/3842 "feat(specprefill): preserve draft recurrent state at cache boundaries") — On hybrid attention + recurrent models the SpecPrefill draft cache never produced a usable hit: a restored cache was read as empty, and recurrent state was never saved at block boundaries. Two stacked fixes.
- **Merged** · [#3664](https://github.com/jundot/omlx/pull/3664 "fix(responses): route namespace tool groups through to the model and back") — The Responses API dropped `namespace` tool groups, the shape Codex uses for MCP servers, so their tools never reached the model. They now round-trip under their namespace.
- Open · [#3964](https://github.com/jundot/omlx/pull/3964 "feat(specprefill): recover reusable prefix state during idle time") — A sparse prefill leaves no reusable prefix, so an append-heavy session keeps re-prefilling a growing suffix. Rebuilds that state in bounded background slices while the process is idle; off by default.
- Open · [#3811](https://github.com/jundot/omlx/pull/3811 "fix(specprefill): keep selected tokens at their original positions on mRoPE VLMs") — On mRoPE vision-language models, SpecPrefill wrote every selected token after the first at the wrong position. Selected tokens now keep their original positions.
<!-- OSS-SELECTED:END -->

<sub>Status is generated from GitHub by a weekly workflow. The full record is under
[More OSS Contributions](#more-oss-contributions).</sub>

## Featured Systems Work

### [laya-apple](https://github.com/tc3oliver/laya-apple) — adaptive heterogeneous inference on Apple silicon

Serves [Laya](https://github.com/NandhaKishorM/laya) on the MLX GPU and the Apple Neural Engine
at the same time, gated on parity with upstream Laya. Its research traced the rise in GPU tail
latency beside a thread-placed ANE to the finished GPU result waiting for the GIL held by
synchronous Core ML `predict` (GPU return P50 7.67 → 0.14 ms once released, in a 2×2
intervention), which led to [apple/coremltools#2876](https://github.com/apple/coremltools/pull/2876).
v1.5 does not depend on that patch: it runs eligible ANE work through Core ML's asynchronous API,
detects a host-side slow state from its own request trace, and falls back to the known-safe 1.4
path. On one M4 Max:

- GPU result return P50 4.28–8.60 → 0.035–0.043 ms against the 1.4 path.
- 154 production validation episodes; 0 mismatches, routing failures, lost requests or crashes.
- No slow state occurred in those runs. In a separate controlled test, the fallback recovered
  12 of 12 slow episodes, back to 1.4 latency within 164–414 ms.

[Research map](https://github.com/tc3oliver/laya-apple/blob/main/research/README.md) ·
[PyPI](https://pypi.org/project/laya-apple/)

### [llm-inference-systems](https://github.com/tc3oliver/llm-inference-systems) — reproducible LLM inference systems research

What an inference optimization leaves behind for the next request. Three experiments with their
data and figures: a sparse prefill that stops the reusable prefix from advancing, speculative
decoding whose break-even is set by verify-cycle cost rather than acceptance rate, and background
recovery of the reusable state. Threads on inference correctness and SpecPrefill admission
economics continue from them. The recovery mechanism (#3964) and the SpecPrefill fixes above came
out of this work.

[Case study](https://meowcoder.com/work/llm-inference-systems/) ·
[Engineering](https://github.com/tc3oliver/llm-inference-systems/blob/main/ENGINEERING.md)

### [version-aware-code-mcp](https://github.com/tc3oliver/version-aware-code-mcp) — version-aware code retrieval over MCP

Confines code search, call-graph queries and source reads to one repository, branch and revision,
so a coding agent cannot quietly answer from the wrong version. Written in Go.

### Other engineering work

[SignalForge](https://github.com/tc3oliver/signalforge) (self-hosted intelligence pipeline) ·
[deepseek-v4-flash-mi300x](https://github.com/tc3oliver/deepseek-v4-flash-mi300x) (vLLM serving
baseline on AMD MI300X) · [Shouri](https://shouri.app) ·
[AI Coding Skills](https://github.com/tc3oliver/skills)

## Research & Writing

- [study.meowcoder.com](https://study.meowcoder.com) — research notes, in Traditional Chinese.
  Start with [當 prefill 變快，agent 反而變慢](https://study.meowcoder.com/posts/260920-inference-reusable-state/)
  and [償還 reusable state 的債](https://study.meowcoder.com/posts/260921-canonical-state-debt-recovery/).
- [laya-apple research map](https://github.com/tc3oliver/laya-apple/blob/main/research/README.md)
  — the 1.4 → 1.5 line from GIL causality to adaptive fallback, every number linked to its study.
- [llm-inference-systems](https://github.com/tc3oliver/llm-inference-systems) — experiments,
  raw data and the evidence map behind them.

<sub>Python · Objective-C++ · MLX · Core ML · PyTorch · vLLM · ROCm · Go · TypeScript</sub>

## More OSS Contributions

<!-- OSS-AUTO:START -->
17 pull requests to projects I don't maintain: 9 merged · 8 open.

**Apple coremltools** — 1 open

- ○ [#2876](https://github.com/apple/coremltools/pull/2876) Release the GIL during native MLModel prediction

**oMLX** — 5 merged · 6 open

- ✓ [#3685](https://github.com/jundot/omlx/pull/3685) fix(attention): keep SDPA256 prefill on the bounded route
- ✓ [#3842](https://github.com/jundot/omlx/pull/3842) feat(specprefill): preserve draft recurrent state at cache boundaries
- ✓ [#3840](https://github.com/jundot/omlx/pull/3840) fix(specprefill): derive draft cache position from attention layers
- ✓ [#3746](https://github.com/jundot/omlx/pull/3746) fix(ane): avoid impossible sequence-length guidance below the ANE minimum
- ✓ [#3664](https://github.com/jundot/omlx/pull/3664) fix(responses): route namespace tool groups through to the model and back
- ○ [#3964](https://github.com/jundot/omlx/pull/3964) feat(specprefill): recover reusable prefix state during idle time
- ○ [#3962](https://github.com/jundot/omlx/pull/3962) test: reset the image decode cache between tests
- ○ [#3811](https://github.com/jundot/omlx/pull/3811) fix(specprefill): keep selected tokens at their original positions on mRoPE VLMs
- ○ [#3792](https://github.com/jundot/omlx/pull/3792) fix(specprefill): remove the RoPE patch when a prefill is requeued after OOM
- ○ [#3762](https://github.com/jundot/omlx/pull/3762) feat(anthropic): accept per-request SpecPrefill overrides on /v1/messages
- ○ [#3756](https://github.com/jundot/omlx/pull/3756) fix(specprefill): preserve the full static system/tool prefix

**Other projects** — 4 merged · 1 open

- ✓ [NandhaKishorM/laya#260](https://github.com/NandhaKishorM/laya/pull/260) docs: add laya-apple to Community Tools
- ✓ [eiei114/pi-model-fallback#64](https://github.com/eiei114/pi-model-fallback/pull/64) fix(error-status): parse "Error: &lt;status&gt;" with no colon after the status
- ✓ [DrJuChunKoO/TransPal-gemini-transcriber#1](https://github.com/DrJuChunKoO/TransPal-gemini-transcriber/pull/1) feat: add resume-from-interruption support for long audio transcriptions
- ✓ [Baseflow/screenrecorder#9](https://github.com/Baseflow/screenrecorder/pull/9) fix: fix the black background
- ○ [ray-project/llmperf#100](https://github.com/ray-project/llmperf/pull/100) feat: Support reasoning\_content in OpenAI chat completions streaming response

<details>
<summary>Superseded, not counted</summary>

- [jundot/omlx#3793](https://github.com/jundot/omlx/pull/3793) feat(specprefill): recover reusable prefix state during idle time — replaced by [#3964](https://github.com/jundot/omlx/pull/3964), [#3962](https://github.com/jundot/omlx/pull/3962)

</details>
<!-- OSS-AUTO:END -->
