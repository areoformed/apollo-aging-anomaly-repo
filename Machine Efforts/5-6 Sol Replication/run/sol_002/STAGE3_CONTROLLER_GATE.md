# sol_002 Stage 3 controller gate

Gate time: 2026-07-23T09:04:03Z

## Decision

Pass. The authorized post-lock reconciliation is complete.

Both locked conclusions remain immutable. The canonical repaired Stage 3 is
under `stage3/`; the initial completed version is preserved under
`stage3_pre_controller_repair/`.

## Narrow result

The reconciliation leaves the two locked, estimand-specific classifications
unchanged:

- `SURVIVAL: NOT_DETECTED / HIGHER`
- corrected unrestricted `PUBLIC FUNCTION: NOT_DETECTED / HIGHER`

It weakens the broad claim that no descriptive anomaly appears under any
reasonable late-life public-activity proxy. On the shared age-80 risk set:

| Endpoint rule | Apollo | Other | Difference | 95% interval |
|---|---:|---:|---:|---:|
| Corrected strict Sol rule | 3/22 | 2/35 | +7.9 pp | -7.7 to +28.0 pp |
| Reference Space Grandpa | 21/22 | 24/35 | +26.9 pp | +5.4 to +43.9 pp |

Every strict Sol positive is also reference-positive. The 40 additional
reference positives make this a construct/ascertainment discrepancy rather
than contradictory person-level evidence.

## Survival

The harmonized common-landmark result is effectively identical to the blind
result:

- Apollo-minus-other 50-year RMST: `+0.670028147` years;
- 50,000-bootstrap 95% interval: `-5.088314852` to `+6.098816053`.

The three reference-only high-speed pilots cannot change this result because
they are outside the harmonized scope and the two early deaths occur before
the 1973 landmark.

## Secondary correction

`DEV-20260723-13` corrects only the retrospective birth-origin
`OTHER_AVAILABLE` description:

- locked Stage 2 erroneous set: 66;
- frozen accident-excluded set: 54;
- excluded pre-1970 accidents: 12;
- post-1973 identity with `OTHER_ALL`: exact, 53 people;
- age-80 identity with `OTHER_ALL`: exact, 35 people.

No primary result changes.

## Validation

- Experimenter validation passed in the neutral runtime.
- Independent controller validation passed without importing experimenter
  code and reproduced the RMST, both public-endpoint contrasts and intervals,
  three 50,000-replicate bootstraps, corrected `OTHER_AVAILABLE` membership,
  and six birth-origin KM readouts.
- All reference, archive, and conclusion hashes pass under their recorded
  runtime/archive manifests.

## Hashes

- initial Stage 3 launch:
  `191ae994389a9ff56af3c48b87d4bbb1b473c94178ace9827ac7978dcceea490`
- approved reference manifest:
  `eeb3244a1885d601718634509db2cf05aa00f59be72a4b74b37b357ad4e3cebe`
- controller repair message:
  `3101dbe7b7a8bd0848146b00318d8d754517658a1a5e7929fbf8b5754075f2cd`
- preserved initial Stage 3 manifest:
  `fb5af5e314803d03a227fec4e3cf78e6778023a0e7e4bcfcd3ea86ec6464a309`
- canonical repaired Stage 3 manifest:
  `49177788a2459fff0833f6840dd814ff8933bd38e68d41b784447c160e6cde34`
- independent controller validator:
  `6283655bb48bd681a6d48965b4be5a70cc0bcd53ff39ca6af1d6c2cc95143841`
- repaired reconciliation:
  `4baf032122a74af70e9bdc873b845ae7a1c3266f1723a3e15307a7934b22d786`
- repaired harmonized results:
  `d783ff810392d9620e665204e7a43e3289b0aaf8663b7e61a04c13c85cdbd462`
- repaired `OTHER_AVAILABLE` correction:
  `df975557f57c94bee35210aaaec5bd5074a2af309ba1e5123b13501aec781f62`
- repaired completion file:
  `ab6d31ce5c50a79c63314d35283483c2d399392f5bf2867b2afba3deb57c6f1d`

## Runtime usage

Stage 3 plus its narrow repair added 9,072,066 input tokens, of which
8,365,056 were cached, plus 74,123 output tokens and 25,860 reasoning-output
tokens to the persistent clean thread.

## Close-out

Stage 3 is complete. No further protocol stage remains. Future work may
interpret, edit the article, or design a differently powered endpoint audit,
but must not be described as part of this blind replication.

