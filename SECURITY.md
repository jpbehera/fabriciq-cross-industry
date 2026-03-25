# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, **please do not open a public issue**.

Instead, report it privately using one of these methods:

1. **GitHub Private Vulnerability Reporting** — Go to the [Security tab](https://github.com/jpbehera/fabriciq-cross-industry/security/advisories/new) of this repository and click **"Report a vulnerability"**.
2. **Email** — Contact the maintainer directly at the email listed on the [GitHub profile](https://github.com/jpbehera).

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 5 business days
- **Fix or mitigation**: Dependent on severity, targeting 30 days for critical issues

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` branch (latest) | Yes |
| All other branches | No |

## Security Controls

This repository implements Zero Trust for AI (ZT4AI) security controls. See [SECURITY_README.md](SECURITY_README.md) for detailed documentation of:

- Input validation and injection prevention
- PII/PHI column exclusion from auto-generated measures
- Prompt injection defenses for AI agents
- URL allowlisting for external sources
- Credential management practices
- Audit logging

## Credential Safety

- **No secrets, tokens, API keys, or credentials should ever be committed** to this repository.
- All sensitive values use `<YOUR_...>` placeholders.
- Runtime credentials are obtained via `DefaultAzureCredential`, `InteractiveBrowserCredential`, or `notebookutils.credentials.getToken()`.
- Environment variables and Azure Key Vault are used for configuration.

## Sample Data Disclaimer

All data in the `datasets/` directory is **entirely fictional**. Names, email addresses, phone numbers, and company references are synthetic and do not represent real individuals or organizations. Phone numbers use the `555-0xxx` reserved range, and email addresses use `.example` or fictional domains per [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606).
