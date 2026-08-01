# Security policy

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | Yes                |

## Reporting a vulnerability

If you discover a security issue in Evident, please report it privately.

**Preferred contact:** open a private security advisory on the GitHub
repository, or email the maintainer listed in package metadata
(`martisoura@gmail.com`).

Please include:

- A description of the issue and its impact
- Steps to reproduce, or a proof of concept if available
- Affected package(s) and versions if known

You should receive an acknowledgment within 7 days. We will work with you on
a fix and coordinated disclosure timeline.

## Scope notes

Evident processes governance artifacts (documents, manifests, registry
metadata) into an evidence graph and evaluates deterministic rules against
that graph. It is not a network service by default. Nonetheless, please
report issues involving:

- Unsafe deserialization or path handling in adapters
- Injection risks when generating reports from untrusted artifact content
- Privilege or isolation concerns in future provenance/context packages

Do not report:

- Missing compliance features or regulatory interpretations
- Social-engineering scenarios outside the library boundary
