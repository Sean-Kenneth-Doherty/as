# Stem Automail Reconfiguration Trace

Status: third schematic-linked Universal Cell trace, 2026-05-17.

This artifact adds a small reconfiguration witness to the P7 schematic evidence
path. The first two traces cover fixed-role wire and processor behavior. This
trace covers one stem automail command from the existing AS Universal Cell
probe.

The structured artifact lives in
`schematics/stem_automail_reconfiguration_trace.json`.

## Trace Shape

The stem starts with:

```json
{
  "role": "stem",
  "memory": "right",
  "automail": "pl",
  "control": [1],
  "buffer": [0]
}
```

The recorded automail flow is:

```text
automail[pl] -> role proc
automail[pl] -> memory left
automail[pl] consumed -> _
```

Running that cell through `step_stem_cell` produces status
`automail-reconfigured`, role `proc`, memory `left`, automail `_`, and clears
the control and buffer fields. The validator recomputes that result instead of
trusting the JSON record.

## Boundary

This trace covers only the explicit automail subset already present in
`step_stem_cell`. It does not model full PRC stem input classification, command
construction, buffer processing, target routing, or dynamic circuit
reconfiguration.

## Verification

Run:

```sh
python -m unittest tests.test_stem_automail_reconfiguration_trace
```

The test validates schema reuse, automail target role and memory, automail
consumption, PRC witness references, and replay through the existing Universal
Cell stem probe.
