---
description: Automated release workflow - Docker build, changelog, version bump, tag, and GitHub release
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[major|minor|patch|x.y.z] [--local-docker]"
---

# Release Workflow

Automate the complete release process including Docker image publishing.

## Current State

Gather context before proceeding:

- Current version: !`cat VERSION`
- Git status: !`git status --short`
- Last 3 tags: !`git tag --sort=-v:refname | head -3`
- Commits since last tag: !`git log $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~20")..HEAD --oneline`
- Docker buildx available: !`docker buildx version 2>/dev/null | head -1 || echo "Not installed"`

## Docker Image Strategy

This project publishes to: `ghcr.io/greogory/hibp-checker`

**Two approaches available:**

### Option A: GitHub Actions (Default - Recommended)
When you push a tag like `v2.1.0`, the `.github/workflows/docker-publish.yml` workflow automatically:
- Builds multi-platform images (linux/amd64, linux/arm64)
- Pushes to GHCR with tags: `2.1.0`, `2.1`, `2`, `latest`, and SHA
- Generates artifact attestation

**Pros**: No local Docker needed, consistent multi-platform builds
**Cons**: Must wait ~5 min for CI to complete

### Option B: Local Docker Build (--local-docker flag)
Build and push locally before creating the git release.

**Pros**: Verify image works before release, immediate
**Cons**: Requires local Docker + GHCR auth, single-platform unless buildx configured

## Workflow Steps

### 1. Validate State

- Check if working tree is clean (no uncommitted changes)
- If there are uncommitted changes, STOP and ask user to commit or stash first
- Verify we're on the main branch

### 2. Determine Version

The user provided: `$ARGUMENTS`

**Parse arguments:**
- Look for version specifier: `major`, `minor`, `patch`, or `x.y.z`
- Look for `--local-docker` flag to enable local Docker build

**If argument is "major", "minor", or "patch":**
- Read current version from `VERSION` file
- Calculate new version based on semver rules:
  - `major`: X.0.0 (breaking changes)
  - `minor`: x.Y.0 (new features)
  - `patch`: x.y.Z (bug fixes)

**If argument is a specific version (x.y.z):**
- Use that exact version

**If no version argument provided:**
- Analyze commits since last tag using conventional commit prefixes:
  - Any `BREAKING CHANGE:` or `!:` → suggest major
  - Any `feat:` → suggest minor
  - Only `fix:`, `docs:`, `chore:`, etc. → suggest patch
- Present suggestion to user and ask for confirmation

### 3. Local Docker Build (if --local-docker specified)

**Only if user passed `--local-docker`:**

1. Verify Docker is running: `docker info`
2. Verify GHCR login: `docker login ghcr.io` (prompt if needed)
3. Build with buildx for multi-platform:
   ```bash
   docker buildx build \
     --platform linux/amd64,linux/arm64 \
     -t ghcr.io/greogory/hibp-checker:NEW_VERSION \
     -t ghcr.io/greogory/hibp-checker:latest \
     --push \
     .
   ```
4. If buildx not available, fall back to single-platform:
   ```bash
   docker build -t ghcr.io/greogory/hibp-checker:NEW_VERSION \
                -t ghcr.io/greogory/hibp-checker:latest .
   docker push ghcr.io/greogory/hibp-checker:NEW_VERSION
   docker push ghcr.io/greogory/hibp-checker:latest
   ```
5. Verify image was pushed: `docker pull ghcr.io/greogory/hibp-checker:NEW_VERSION`

**If Docker build/push fails, STOP and do not continue with release.**

### 4. Update CHANGELOG.md

- Read the current CHANGELOG.md
- Find the `## [Unreleased]` section
- If [Unreleased] section is empty or only has whitespace, STOP and warn user
- Rename it to `## [NEW_VERSION] - YYYY-MM-DD` (use today's date)
- Add a new empty `## [Unreleased]` section above it with standard headers:
  ```markdown
  ## [Unreleased]

  ### Added

  ### Changed

  ### Fixed
  ```
- Update the comparison link at the bottom if it exists

### 5. Update VERSION File

- Write the new version number to the `VERSION` file
- Ensure no trailing newline issues

### 6. Create Release Commit

Create a commit with message:
```
chore(release): bump version to X.Y.Z

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### 7. Create Git Tag

- Create an annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- Annotated tags are required for GitHub releases

### 8. Push to Remote

- Push the commit: `git push`
- Push the tag: `git push origin vX.Y.Z`

**Important**: If NOT using --local-docker, remind user:
> "GitHub Actions will now build and push the Docker image. Monitor at:
> https://github.com/greogory/hibp-checker/actions"

### 9. Create GitHub Release

Use the `gh` CLI to create a release:

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes "RELEASE_NOTES_HERE"
```

**For release notes:**
- Extract content between `## [X.Y.Z]` and the next `## [` header from CHANGELOG.md
- Include Docker pull instructions at the bottom:
  ```markdown
  ## Docker

  docker pull ghcr.io/greogory/hibp-checker:X.Y.Z
  ```

### 10. Post-Release Verification

After release is complete, display:
- Link to GitHub release
- Link to GitHub Actions workflow (for Docker build status)
- Docker pull command
- Remind user to verify Docker image is available after CI completes (~5 min)

## Safety Checks

Before each destructive operation, confirm with the user:
- Before Docker push (if --local-docker)
- Before pushing to remote
- Before creating GitHub release

## Error Handling

- If any step fails, STOP and report the error
- Do NOT continue with subsequent steps after a failure
- Provide clear instructions for manual recovery if needed
- For Docker failures: suggest checking `docker login ghcr.io` status

## Example Usage

```bash
# Standard release (GitHub Actions builds Docker)
/release patch      # 2.0.3 → 2.0.4
/release minor      # 2.0.3 → 2.1.0
/release major      # 2.0.3 → 3.0.0
/release 2.1.0      # Set exact version
/release            # Auto-detect from commits

# With local Docker build first
/release patch --local-docker
/release 2.1.0 --local-docker
```

## Rollback Instructions

If something goes wrong after partial completion:

**If tag was created but not pushed:**
```bash
git tag -d vX.Y.Z
```

**If tag was pushed:**
```bash
git push --delete origin vX.Y.Z
git tag -d vX.Y.Z
```

**If commit was made:**
```bash
git reset --soft HEAD~1
```

**If GitHub release was created:**
```bash
gh release delete vX.Y.Z --yes
```

**If Docker image was pushed:**
- Delete from GHCR web UI: https://github.com/users/greogory/packages/container/hibp-checker/versions
