# ML

The prediction subsystem classifies parsed article text into incident categories.

## Components

- Local BERT-based models for deterministic category predictions
- Predictor registry to support multiple predictor backends
- Optional LLM-backed path for specific classification strategies

## Pipeline Integration

1. Parsing produces normalized article text.
2. Prediction runs in batches across active incident types.
3. Confidence scores are stored and used for acceptance/rejection workflow.

## Operational Considerations

- Keep models and tokenizer configs versioned and reproducible.
- Track predictor behavior changes with tests and rollout notes.
- Validate minimum text quality before prediction.

## Change Guidance

When adding a predictor:

1. Register predictor in the routing/registry layer.
2. Define expected input and output shape.
3. Add tests for batch behavior and decision thresholds.
4. Document required credentials and runtime assumptions.

## See Also

- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Domain model: [DOMAIN.md](DOMAIN.md)
- Security: [SECURITY.md](SECURITY.md)
