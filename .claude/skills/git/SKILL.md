---
name: git-safe-workflow
description: Safe and practical Git workflow for Playwright Page Object Generator project - requires explicit user approval for all repository-modifying operations
---

# Safe Git Workflow for Playwright Page Object Generator

## ⚠️ Core Safety Principles

**This skill enforces safe Git operations.** Claude performs Git actions only when:
1. User explicitly requests it
2. All safety checks pass
3. Changes are reviewed before execution

Claude will NEVER automatically:
- Initialize repositories
- Create commits
- Execute push/force-push
- Delete branches or commits
- Perform destructive operations

---

## 1. Git Initialization

### ❌ DO NOT Auto-Initialize

```bash
# ❌ This will NOT run automatically
git init
```

### ✅ User Request Required

Only initialize when user explicitly asks:
```
"Initialize this as a git repository"
"git init please"
```

**Before initializing:**
1. Confirm current directory is correct
2. Check if `.git` already exists
3. Ask if user wants to preserve any existing work
4. Never assume state

---

## 2. Commit Workflow

### Safety Checklist (ALWAYS)

Before ANY commit, execute in order:

```bash
git status                    # See all changes
git diff                      # Review unstaged changes
git diff --staged            # Review staged changes
```

### Pre-commit Verification

✅ Do:
- Review each file being committed
- Verify changes match commit scope
- Scan for secrets/credentials
- Run tests if relevant
- Check for debug code/console logs

❌ Don't:
- Commit random files from `git add .`
- Commit unrelated changes together
- Assume files are safe
- Skip the diff review

### Creating a Commit

Only execute `git commit` after:
1. User explicitly requests: "Create a commit" / "Make a commit"
2. All safety checks complete
3. User approves staged changes

**Commit message format** (Conventional Commits):
```
feat(scope): brief description
fix(scope): description
refactor(scope): description
test(scope): description
docs(scope): description
chore(scope): description
```

Example:
```
feat(parser): add BeautifulSoup HTML parsing support

- Parse HTML with html5lib backend
- Extract element tree with attributes
- Handle malformed HTML gracefully
```

### ❌ Never Automatically Add

Do NOT auto-add these to commits:
- `.env` files
- `credentials.json`, `secrets.json`
- `*.key`, `*.pem`
- `__pycache__/`, `.pytest_cache/`
- Build artifacts
- IDE config files (unless explicitly in scope)

---

## 3. Push Operations

### ❌ NEVER Auto-Push

```bash
# ❌ Will NOT execute without explicit approval
git push
git push origin main
git push --force
```

### Before Push Verification

**User must explicitly request**: "Push changes" / "Push to origin"

Then execute checks:
```bash
git status                           # Confirm clean working tree
git log origin/HEAD..HEAD --oneline # Show unpushed commits
git log -1 --format=fuller          # Show last commit details
git config --get remote.origin.url  # Confirm remote URL
```

### Push Restrictions

❌ Forbidden without explicit separate approval:
- `git push --force`
- `git push --force-with-lease`
- `git push -u origin feature/...` (first time to new branch)

✅ Safe operations after user confirms:
- `git push origin main`
- `git push origin feature/name`

**Final confirmation before push:**
```
About to push X commits to origin/main:
- [list commits]

Remote: [URL]
Branch: [branch name]

Proceed? (yes/no)
```

---

## 4. Dangerous Operations (FORBIDDEN)

These NEVER execute without explicit user confirmation:

```bash
# ❌ Destructive - requires explicit approval
git reset --hard                  # Discard ALL changes
git reset --hard origin/main      # Reset to remote

# ❌ Force operations - requires explicit approval  
git push --force                  # Force push (can overwrite upstream)
git push --force-with-lease       # Safer force, still dangerous

# ❌ History rewriting - requires explicit approval
git rebase                        # Rewrite commit history
git rebase -i HEAD~5              # Interactive rebase
git commit --amend                # Modify last commit

# ❌ Cleanup - requires explicit approval
git clean -fd                     # Delete untracked files
git branch -D feature/x           # Force delete branch

# ❌ File operations - requires explicit approval
git checkout -- src/file.py       # Discard file changes
git restore src/file.py           # Discard file changes
```

### When These Are Needed

If user requests a dangerous operation:
1. **Explain the risk clearly**
2. **Show what will be lost**
3. **Suggest safe alternatives**
4. **Wait for explicit confirmation** before executing

Example:
```
⚠️ DANGEROUS OPERATION REQUESTED

You requested: git reset --hard HEAD~1

This will:
- ❌ Delete the last commit permanently
- ❌ Discard all changes in that commit
- ❌ Cannot be undone easily

Current commit:
- [commit message]
- [files changed]

Alternatives:
1. git revert HEAD (safer - creates new commit that undoes changes)
2. git reset HEAD~1 (soft - keeps changes, unstages them)

Confirm you want to proceed? (yes/no)
```

---

## 5. Branch Management

### ✅ Safe Branch Operations

User can request:
```
"Create a feature branch for HTML parsing"
"Create a bugfix branch for duplicate names"
```

**Before creating branch:**
1. Check current branch: `git branch -v`
2. Check for uncommitted changes: `git status`
3. Confirm base branch is up to date: `git fetch origin`

**Recommended branch naming:**
```
feature/feature-name              # New feature
fix/bug-description              # Bug fix
refactor/what-changed            # Refactoring
test/what-you-test               # Test additions
docs/topic                       # Documentation
chore/dependency-update          # Maintenance
```

Example workflow:
```bash
# 1. Confirm branch strategy with user
git status                        # Check current state
git branch -v                     # Show all branches

# 2. Create new branch
git checkout -b feature/html-parser

# 3. Report to user
Current branch: feature/html-parser
Base: main
Ready to work on this feature.
```

### ❌ NEVER Auto-Manage Branches

- Do NOT delete branches automatically
- Do NOT switch branches without request
- Do NOT create branches for random tasks

---

## 6. Merge Conflicts

### When Conflicts Occur

1. **STOP - do not auto-resolve**
2. Show the conflicted section
3. Explain both versions
4. List resolution options
5. Wait for user guidance

Example:
```
⚠️ MERGE CONFLICT

File: src/locator_selector.py
Lines: 42-67

<<<<<<< HEAD (current branch)
    # Strategy: priority-based approach
    if element.has_role:
        return f"page.get_by_role('{element.role}')"
=======
    # Strategy: attribute-based approach  
    if element.has_id:
        return f"page.locator('#{element.id}')"
>>>>>>> feature/attribute-strategy

Your version (HEAD):
- Uses semantic roles first
- Better for accessibility

Their version (feature/attribute-strategy):
- Uses element IDs first
- More specific targeting

How would you like to resolve this? 
Provide guidance or approve one version.
```

❌ Never:
- Auto-choose one side
- Delete changes
- Merge without showing conflict

---

## 7. GitHub Operations

### ❌ NEVER Auto-Execute

```bash
# These require explicit user request AND confirmation
gh repo create
gh pr create
gh pr merge
gh pr close
gh issue create
gh release create
git push origin --delete branch-name
```

### Allowed Only With Explicit Request

User must explicitly say:
```
"Create a PR"
"Merge the PR"
"Delete the remote branch"
```

### PR Creation Workflow

When user requests PR:

1. **Verify commits:**
   ```bash
   git log origin/main..HEAD --oneline
   ```

2. **Confirm ready for PR:**
   - All commits on feature branch
   - Working tree clean
   - Latest from main fetched

3. **Show PR details before creating:**
   ```
   PR Title: feat: implement HTML parser
   Target Branch: main
   Source Branch: feature/html-parser
   
   Commits (3):
   - feat(parser): add BeautifulSoup support
   - test(parser): add edge case tests
   - docs(parser): update README
   ```

4. **Wait for user confirmation**

---

## 8. Secrets Protection

### ❌ NEVER Commit These Files

```
.env
.env.local
.env.*.local
credentials.json
secrets.json
.credentials
private_key.pem
*.key
config.yaml (if contains secrets)
token.txt
password.txt
```

### Scanning Before Commit

Before adding ANY file to commit:
1. Check filename against secret patterns
2. If suspicious, read first few lines
3. Look for patterns: `password=`, `token:`, `api_key`, `secret:`
4. Ask user if unsure

Example:
```
⚠️ Suspicious file detected

File: src/config.py

Content snippet:
```
PLAYWRIGHT_API_KEY = "pk_live_..."  # ← Credential detected!
DATABASE_PASSWORD = "secret123"      # ← Password detected!
```

This file contains secrets and should NOT be committed.

Options:
1. Use .env file (add to .gitignore)
2. Use environment variables
3. Remove secrets before committing

Proceed without this file? (yes/no)
```

---

## 9. Status Reporting

### After Each Git Operation

Report:
```
✅ Operation: [what was done]
📁 Current branch: [branch name]
🔄 Status: [git status output]
📝 Last commit: [hash + message]
📤 Push status: [if applicable]
```

Example:
```
✅ Commit created successfully

📁 Current branch: feature/html-parser
🔄 Status: Working tree clean
📝 Last commit: a3f2b1c - feat(parser): add BeautifulSoup support
📤 Not pushed yet (use 'git push origin feature/html-parser' when ready)

Files committed:
- src/parser.py
- tests/test_parser.py
```

### ❌ Never Claim Success Without Verification

Verify command actually succeeded:
```bash
# After commit
git log -1 --oneline

# After push  
git log origin/HEAD..HEAD --oneline  # Should be empty
```

---

## 10. Project-Specific Context

### Playwright Page Object Generator

**Stack:**
- Python 3.8+
- Playwright for Python
- pytest for testing
- BeautifulSoup4 for HTML parsing

**Project structure:**
```
.
├── src/
│   ├── parser.py
│   ├── locator_selector.py
│   ├── generator.py
│   └── utils.py
├── tests/
├── main.py
├── requirements.txt
├── CLAUDE.md
└── README.md
```

**Locator strategy** (for commit examples):
```
1. get_by_test_id()     - data-testid attribute
2. get_by_role()        - semantic HTML roles
3. get_by_label()       - form labels
4. get_by_placeholder() - input placeholders
5. get_by_text()        - visible text content
6. CSS selector         - stable selectors
7. XPath                - last resort
```

### Example Commits for This Project

```
feat(parser): add HTML5 parsing with BeautifulSoup

- Use html5lib backend for flexible parsing
- Handle unclosed tags and malformed HTML
- Extract element tree while preserving structure

feat(locator): implement priority-based selector strategy

Selectors chosen in order:
1. get_by_role() - semantic HTML
2. get_by_label() - form labels  
3. get_by_placeholder() - input attributes
4. get_by_text() - visible content
5. CSS selector - as fallback

fix(generator): handle duplicate element names

When multiple elements have same description:
- Append index suffix (button_1, button_2)
- Generate unique property names
- Include warning in docstring

test(parser): add edge case coverage

- Unclosed HTML tags
- Deeply nested elements
- Special characters in attributes
- Mixed element types
```

---

## 11. Workflow Checklist

### Before Any Git Operation

- [ ] User explicitly requested the operation
- [ ] Current directory is correct
- [ ] `git status` shows expected state
- [ ] No uncommitted work will be lost
- [ ] No secrets in changes
- [ ] Branch name is correct
- [ ] Remote URL is correct
- [ ] User confirmed the action

### After Git Operation

- [ ] Verify command succeeded (`echo $?` or check output)
- [ ] Report status to user
- [ ] Show current branch and changes
- [ ] Suggest next steps
- [ ] Do NOT claim success without verification

---

## 12. Safe Alternatives to Dangerous Operations

### Instead of `git reset --hard`

```bash
# ✅ SAFE: Soft reset (keeps changes unstaged)
git reset HEAD~1

# ✅ SAFE: Create undo commit  
git revert HEAD

# ✅ SAFE: Stash and inspect
git stash
```

### Instead of `git push --force`

```bash
# ✅ SAFE: Check what changed
git log origin/main..HEAD

# ✅ SAFE: Force with lease (safer)
git push --force-with-lease  # Still requires approval

# ✅ SAFE: Rebase locally first
git fetch origin
git rebase origin/main       # Local rebase only
git push origin              # Regular push after
```

### Instead of `git commit --amend`

```bash
# ✅ SAFE: New commit that undoes
git revert HEAD

# ✅ SAFE: Create new commit
git commit -m "fix: ..."
```

### Instead of `git branch -D`

```bash
# ✅ SAFE: Regular delete (checks if merged)
git branch -d feature/name

# ✅ SAFE: On remote
git push origin --delete feature/name  # After approval
```

---

## 13. Final Report Template

After Git operations, use this format:

```
═══════════════════════════════════════════════════
✅ GIT OPERATION SUMMARY
═══════════════════════════════════════════════════

Operation: [git command executed]
Status: ✅ Success / ❌ Failed

Current state:
  Branch: [branch name]
  Changes: [git status output or "Clean"]
  
Results:
  [Specific outcome - commits, files, etc.]

Next steps:
  [What user can do next]

═══════════════════════════════════════════════════
```

Example:
```
═══════════════════════════════════════════════════
✅ GIT OPERATION SUMMARY  
═══════════════════════════════════════════════════

Operation: Create feature branch and initial commits
Status: ✅ Complete

Current state:
  Branch: feature/html-parser
  Changes: Clean (working tree unmodified)
  
Results:
  ✓ Created branch from main
  ✓ Committed: 3f7a2b1 - feat(parser): add parser.py
  ✓ Committed: 8e9c1d2 - test(parser): add test_parser.py
  
Next steps:
  1. Make more changes and commits
  2. Test locally with pytest
  3. When ready: git push origin feature/html-parser
  4. Create pull request for review

═══════════════════════════════════════════════════
```

---

## 14. Summary: What This Skill Does

✅ **ALLOWS:**
- Viewing status and diffs
- Creating branches (on request)
- Reviewing commits
- Planning Git operations
- Explaining Git concepts
- Helping with conflict resolution

❌ **REQUIRES EXPLICIT APPROVAL FOR:**
- Creating any commit
- Pushing changes
- Deleting branches/commits
- Force operations
- Amending commits
- Rebasing
- Merging

❌ **NEVER DOES:**
- Auto-initialize repositories
- Auto-commit changes
- Auto-push code
- Auto-delete files/branches
- Execute destructive operations without approval
- Commit files with secrets
- Merge conflicts automatically
