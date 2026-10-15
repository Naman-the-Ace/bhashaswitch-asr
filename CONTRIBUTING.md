# Contributing to BhashaSwitch

Thank you for contributing to BhashaSwitch.

## Guidelines

1. **Test Coverage**:
   - Every normalization edge case (Devanagari matras, conjuncts, nuktas) and metric calculation must have corresponding unit tests in `tests/`.
   - Run tests before submitting commits:
     ```bash
     pytest -v
     ```

2. **Benchmark Integrity**:
   - Real model outputs must be recorded with exact model identifiers, git commit hashes, and decoding parameters. Never invent benchmark numbers.
