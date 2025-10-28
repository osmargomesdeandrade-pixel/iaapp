Release v0.1.0 — Draft

Tag: v0.1.0

Summary:
- First release of the AI App Generator. Includes templates, CLI and a Flask UI.

Suggested release notes (short):
This release introduces a template-based application generator with optional LLM augmentation. It includes safety controls, a review UI and unit tests. See CHANGELOG.md for details.

How to publish this release via gh CLI:

gh release create v0.1.0 --title "v0.1.0" --notes-file .github/release-draft.md
