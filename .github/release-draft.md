Release v0.1.4 — Draft

Tag: v0.1.4

Summary:
- Documentation and CI fixes; add GitHub Pages docs and improve workflows.

Highlights:
- Added GitHub Pages documentation (`docs/index.md`, `docs/QUICKSTART.md`) and `.nojekyll`.
- Improved Pages workflow and added sanity checks; iterated on permissions.
- Created example generated project `demo_generated/demo_ai` and fixed linting issues.
- CI: ensured flake8 and mypy pass in the latest runs.

Suggested release notes (short):
This patch release adds documentation for the AI App Generator, improves CI/workflows, and includes small fixes to templates and generated examples. See CHANGELOG.md and docs/QUICKSTART.md for usage details.

How to publish this release via gh CLI:

gh release create v0.1.4 --title "v0.1.4" --notes-file .github/release-draft.md
