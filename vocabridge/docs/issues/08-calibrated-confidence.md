# Calibrate confidence scores from review history
Labels: trust, enhancement, v0.2

## Why

A confidence of 0.9 is only useful if roughly 90% of such suggestions turn out correct. Research on LLM-based matching reports systematic overconfidence that simple post-hoc calibration (e.g. temperature or Platt scaling) reduces substantially. vocabridge already records every accept/reject decision, which is exactly the labelled data calibration needs.

## What

- `vocabridge calibrate <mapping files...> -o calibration.json`: collect (raw confidence, accepted?) pairs per `method`; fit a monotonic calibration (isotonic regression or Platt scaling, standard library or a tiny dependency).
- `suggest --calibration calibration.json` stores both `raw_confidence` and calibrated `confidence`, and adds an `Evidence` entry naming the calibration file and sample size.
- `vocabridge trust-report` prints a reliability table: confidence bucket → share accepted, and Expected Calibration Error.
- Refuse to calibrate on fewer than ~30 decisions; say so.

## Acceptance

- Unit tests with synthetic decisions where the right calibration is known.
- Mapping format stays backward compatible (`raw_confidence` optional).
