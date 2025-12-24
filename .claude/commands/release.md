---
description: Automated release workflow - changelog, version bump, tag, and GitHub release
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[major|minor|patch] or [x.y.z]"
---

# Release Workflow

Automate the complete release process following semantic versioning and Keep a Changelog conventions.

## Current State

Gather context before proceeding:

- Current version: !`cat VERSION`
- Git status: !`git status --short`
- Last 3 tags: !`git tag --sort=-v:refname | head -3`
- Commits since last tag: !`git log $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~20")..HEAD --oneline`

## Workflow Steps

Execute these steps in order:

### 1. Validate State

- Check if working tree is clean (no uncommitted changes)
- If there are uncommitted changes, STOP and ask user to commit or stash first
- Verify we're on the main branch

### 2. Determine Version

The user provided: `$ARGUMENTS`

**If argument is "major", "minor", or "patch":**
- Read current version from `VERSION` file
- Calculate new version based on semver rules:
  - `major`: X.0.0 (breaking changes)
  - `minor`: x.Y.0 (new features)
  - `patch`: x.y.Z (bug fixes)

**If argument is a specific version (x.y.z):**
- Use that exact version

**If no argument provided:**
- Analyze commits since last tag using conventional commit prefixes:
  - Any `BREAKING CHANGE:` or `!:` → suggest major
  - Any `feat:` → suggest minor
  - Only `fix:`, `docs:`, `chore:`, etc. → suggest patch
- Present suggestion to user and ask for confirmation

### 3. Update CHANGELOG.md

- Read the current CHANGELOG.md
- Find the `## [Unreleased]` section
- Rename it to `## [NEW_VERSION] - YYYY-MM-DD` (use today's date)
- Add a new empty `## [Unreleased]` section above it
- Update the comparison link at the bottom if it exists

### 4. Update VERSION File

- Write the new version number to the `VERSION` file
- Ensure no trailing newline issues

### 5. Create Release Commit

Create a commit with message:
```
chore(release): bump version to X.Y.Z

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### 6. Create Git Tag

- Create an annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- Annotated tags are required for GitHub releases

### 7. Push to Remote

- Push the commit: `git push`
- Push the tag: `git push origin vX.Y.Z`

### 8. Create GitHub Release

Use the `gh` CLI to create a release:

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes-file <(extract release notes from CHANGELOG for this version)
```

Extract the release notes for this version from CHANGELOG.md (everything between `## [X.Y.Z]` and the next `## [` header).

## Safety Checks

Before each destructive operation, confirm with the user:
- Before pushing to remote
- Before creating GitHub release

## Error Handling

- If any step fails, STOP and report the error
- Do NOT continue with subsequent steps after a failure
- Provide clear instructions for manual recovery if needed

## Example Usage

```
/release patch      # Bump 2.0.3 → 2.0.4
/release minor      # Bump 2.0.3 → 2.1.0
/release major      # Bump 2.0.3 → 3.0.0
/release 2.1.0      # Set exact version
/release            # Auto-detect from commits
```
