# LMCache MP merge-readiness packet workflow

Use this when validating an LMCache/vLLM/SGLang inference-stack PR that needs runtime packet evidence before merge. Keep packet proof, repo state, and blockers separate; do not collapse them into a generic "tests passed" statement.

## Evidence planes to report

- Packet B / lifecycle reuse evidence: workload profile, request count, acceptance status, L0/L1 family coverage, KV/offload claim status, and diagnostic L1 failure counts.
- Packet C / L2 persistence evidence: `/conf` L2 adapter config, server CLI args, L2 metric families, KV `.data` file count, and total persisted bytes.
- CacheBlend evidence: only mark measured if a CacheBlend-specific workload produced CacheBlend metric families, or a dedicated boundary-evidence artifact proves the CacheBlend/L0 lifecycle path exercised with nonzero rows/events. Long-context KV/offload packets alone are not CacheBlend proof.
- Repo state: branch, dirty status, upstream/tracking branch, ahead/behind, and whether a repo was fetched, fast-forwarded/merged, or skipped because dirty.
- Hardware proof: exact provider/GPU packet or Modal volume path when available; otherwise say `not proven` or `blocked`.

## Pitfalls caught in LMCache MP validation

- LMCache MP server does not consume a runner-written `lmcache_l2_config.json` metadata file by itself. Configure FS L2 through the server CLI argument instead, e.g. `--l2-adapter '{"type":"fs","base_path":"..."}'`, then verify `/conf` reports non-empty `l2_adapter_config.adapters` and `num_l2_adapters > 0`.
- `l0_lifecycle` compatibility checks must include block counter metrics as well as timing metrics. Match both `lmcache_mp_l0_block_*_total` and `lmcache_mp.l0_block_*_total`; otherwise packet evidence with block counters can be misclassified as missing lifecycle coverage.
- When summing L1 allocation/read failures from normalized reports, avoid double-counting mirrored data under both `compat.diagnostic_findings` and `kv_report.diagnosis.compat_diagnostic_findings`. Prefer the primary compat findings and only fall back to kv_report diagnosis when compat findings are absent.
- L1 allocation failures under deliberate capacity pressure are diagnostic evidence, not automatically a merge blocker. Report allocation vs read failure counts, cache size/eviction context, and packet failure reasons. If read failures are zero and Packet B remains `candidate_measured`, readiness logic should keep the finding under `diagnostic_findings` / severity `diagnostic` and compute `merge_ready` from blocking blockers only.
- If CacheBlend Prometheus family counts are zero but a dedicated boundary evidence file exists, count CacheBlend as measured only when the artifact has nonzero rows for CacheBlend-relevant events such as `report_block_allocation_received` and `l0_lifecycle_subscriber_processed`; include row/event counts in the report so this does not look like a silent waiver.

## Cleanup/finalization gate

Before handing back an LMCache MP readiness update, run a cleanup pass that separates generated junk from real work:

- Remove macOS metadata (`.DS_Store`, `._*`) from all involved repos and ensure the user's global git excludes include those patterns.
- Format/lint only touched/new files where possible; avoid whole-file churn in legacy files with unrelated style debt.
- Re-run the focused InferGuard readiness tests and LMCache MP observability tests after formatting.
- Regenerate the readiness JSON artifact after cleanup, not before, and report its path plus remaining blocking blockers and diagnostic findings.
- Do not delete untracked but potentially useful artifacts such as analysis docs, prompt exports, packet evidence, or new tests unless the user explicitly says to discard them; list them under `repo_dirty` instead.

## Merge-readiness CLI answer shape

For InferGuard-backed readiness checks, prefer a single machine-readable JSON artifact plus a short human summary:

```bash
PYTHONPATH=src python -m inferguard.cli lmcache-merge-ready \
  --packet-b-dir <packet-b-artifact-dir> \
  --packet-c-dir <packet-c-artifact-dir> \
  --repo vllm=<vllm-path> \
  --repo lmcache=<lmcache-path> \
  --repo sglang=<sglang-path> \
  --output /tmp/lmcache-merge-ready-current.json \
  --json
```

Report:

- `merge_ready: true|false`
- blocking blockers separately from diagnostic findings
- Packet B status/key counts
- Packet C L2 configured status/file bytes/metric family count
- per-repo branch/dirty/ahead/behind
- tests and lint commands used to validate the readiness command itself

If `cacheblend_not_measured` appears, the next action is a dedicated CacheBlend packet/workload or an explicit user decision to defer that coverage; do not claim Packet B/C satisfied CacheBlend coverage.
