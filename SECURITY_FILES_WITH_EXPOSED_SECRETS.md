# 🚨 FILES WITH EXPOSED SECRETS - NEVER COMMIT THESE

## Files Removed from Repository (Contained Hardcoded API Keys)

### ❌ DELETED - Had OpenAI API Keys Hardcoded:
1. **`backend/fix_empty_docs.py`** - Line 53: Hardcoded OpenAI API key
2. **`backend/generate_dealflow_docs.py`** - Line 10: Hardcoded OpenAI API key

These files have been:
- ✅ Deleted from working directory
- ✅ Added to .gitignore
- ⚠️ Still exist in git history (commits before cleanup)

## GitHub Push Protection Issues

When pushing, GitHub detected:
```
- OpenAI API Key in commit 228f8e1e119c144e287beaefa2eed61e260aae7a
  - backend/fix_empty_docs.py:53
  - backend/generate_dealflow_docs.py:10
```

## Action Items to Prevent This Forever

### 1. **IMMEDIATELY Rotate/Revoke Exposed API Keys**
- [ ] Go to OpenAI Dashboard: https://platform.openai.com/api-keys
- [ ] Revoke the exposed key: `sk-proj-5KWAHW2Y...` (shown in deleted files)
- [ ] Generate a new API key
- [ ] Store it in environment variables ONLY

### 2. **Updated .gitignore (Already Done)**
```gitignore
# Example and test files (not for production)
*EXAMPLE*.tsx
*EXAMPLE*.ts
*TEST*.tsx
*_test.tsx

# Files with hardcoded secrets (use env vars instead)
fix_empty_docs.py
generate_dealflow_docs.py
```

### 3. **Git History Cleanup** (If Needed - DANGEROUS)

⚠️ **WARNING**: This rewrites history. Only do this if:
- The exposed keys are critical
- You can coordinate with all developers
- You understand the risks

```bash
# Option A: Remove from all history (NUCLEAR option)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/fix_empty_docs.py backend/generate_dealflow_docs.py" \
  --prune-empty --tag-name-filter cat -- --all

# Option B: BFG Repo Cleaner (easier, safer)
# Download from: https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files fix_empty_docs.py
java -jar bfg.jar --delete-files generate_dealflow_docs.py
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Then force push
git push origin --force --all
```

### 4. **Environment Variable Setup (CORRECT WAY)**

#### In your .env file (NEVER commit this):
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

#### In your Python code:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("OPENAI_API_KEY not set in environment")

# Use the api_key
```

#### In Vercel (for production):
1. Go to Project Settings → Environment Variables
2. Add: `OPENAI_API_KEY` = `your-key`
3. Select environments: Production, Preview, Development

### 5. **Pre-commit Hook to Block Secrets**

Install `detect-secrets`:
```bash
pip install detect-secrets
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

Initialize:
```bash
detect-secrets scan --baseline .secrets.baseline
```

### 6. **Additional Git Hooks**

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Block commits with potential secrets

if git diff --cached | grep -E "sk-[A-Za-z0-9]{20,}|github_pat_|ghp_|AIza[A-Za-z0-9_-]{35}"; then
    echo "❌ ERROR: Potential API key or secret detected!"
    echo "Please remove the secret and use environment variables instead."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Safe Files (Template/Documentation Only)

These files contain references to API keys but are safe:
- ✅ `backend/env.example` - Template with placeholder values
- ✅ `backend/env.supabase.template` - Template file
- ✅ `backend/tests/test_agenda_generator.py` - Uses fake test keys
- ✅ `*.md` files - Documentation examples

## Current Status

✅ **Working directory is clean** - No exposed secrets in current files
✅ **Files added to .gitignore** - Won't be committed again
✅ **Next.js upgraded** - From 14.2.23 to 15.1.3 (security fix)
⚠️ **Git history** - Old commits still contain secrets (rotate keys!)
⏳ **Ready to push** - Once you're satisfied with the cleanup

## Next Steps

1. **Rotate the exposed OpenAI API key** (do this first!)
2. Review this document
3. Add pre-commit hooks (optional but recommended)
4. Push the cleaned code
5. Set environment variables in Vercel

## Prevention Checklist

- [ ] Never hardcode API keys, tokens, or credentials
- [ ] Always use environment variables (.env files)
- [ ] Add .env to .gitignore
- [ ] Use templates (.env.example) with placeholder values
- [ ] Enable GitHub secret scanning (already detected this!)
- [ ] Add pre-commit hooks for extra safety
- [ ] Review code before committing
- [ ] Rotate keys immediately if exposed

---

**Remember**: The best security is prevention. Always use environment variables for secrets!
