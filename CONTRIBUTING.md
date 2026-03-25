# Contributing to FabricIQ Cross-Industry Accelerator

Thank you for your interest in contributing! This document explains how to contribute safely to a public repository that handles sample data across multiple industries.

## Getting Started

1. **Fork** the repository.
2. **Clone** your fork locally.
3. Create a **feature branch** from `main`.
4. Make your changes.
5. Submit a **Pull Request** against `main`.

## Security Requirements

**These are mandatory for all contributions:**

### Never Commit Secrets

- No API keys, tokens, passwords, connection strings, or credentials.
- Use `<YOUR_...>` placeholders for any configurable values (workspace IDs, cluster URIs, etc.).
- If you accidentally commit a secret, **notify the maintainer immediately** — git history retains deleted content.

### Strip Notebook Outputs

Notebook cell outputs can leak runtime tokens, workspace IDs, or data previews.

```bash
# Install once (sets up an automatic git filter):
pip install nbstripout
nbstripout --install
```

This ensures outputs are stripped on every `git add`. The CI pipeline will also reject notebooks with outputs.

### Sample Data Rules

- **No real PII** — use fictional names, addresses, and phone numbers.
- **Phone numbers** — use the `555-0xxx` reserved range.
- **Email addresses** — use `.example` or `.example.org` domains per [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606) (e.g., `j.doe@company.example`).
- **Company names** — use fictional names or add a disclaimer if referencing real companies for illustrative purposes.

### Input Validation

All column names, table names, and identifiers must go through the sanitization functions in `ZT_Security_Utils.ipynb`. Do not bypass these checks.

## Code Style

- **Python**: Follow PEP 8.
- **Notebooks**: Keep cells focused on a single logical step. Add markdown cells to explain intent.
- **SQL/KQL**: Use parameterized queries via the sanitization utilities — never use raw string interpolation with user-controlled values.

## Pull Request Process

1. Ensure the CI security checks (Gitleaks, notebook output check) pass.
2. Update documentation if your change affects the pipeline behavior or security controls.
3. At least one maintainer review is required before merging.
4. Squash commits for a clean history.

## Reporting Security Issues

Do **not** open a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md) for private reporting instructions.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
