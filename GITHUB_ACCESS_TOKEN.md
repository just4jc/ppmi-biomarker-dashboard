# GitHub Personal Access Token Guide

## What is a Personal Access Token?

A GitHub Personal Access Token (PAT) is a secure alternative to using your password for authenticating to GitHub when using the Git command line, GitHub API, or other third-party tools. Think of it as a special password that you can create, revoke, and manage separately from your main GitHub account password.

## When Do You Need a Personal Access Token?

You may need a GitHub Personal Access Token for:

1. **Cloning private repositories** via HTTPS
2. **Pushing code changes** to repositories via HTTPS
3. **Using the GitHub CLI** (`gh` command)
4. **Accessing the GitHub API** programmatically
5. **Creating or managing releases** (like the data files hosted in this repository)
6. **Using GitHub Actions** or other automation tools

## Where to Locate/Create Your Personal Access Token

### Step 1: Navigate to GitHub Settings

1. Log in to your GitHub account at [https://github.com](https://github.com)
2. Click on your **profile picture** in the top-right corner
3. Select **Settings** from the dropdown menu

### Step 2: Access Developer Settings

1. In the left sidebar, scroll down to the bottom
2. Click on **Developer settings** (near the bottom of the menu)

### Step 3: Navigate to Personal Access Tokens

You have two options for token types:

#### Option A: Fine-grained Personal Access Tokens (Recommended - More Secure)
1. Click on **Personal access tokens** in the left sidebar
2. Select **Fine-grained tokens**
3. Click **Generate new token**

#### Option B: Classic Personal Access Tokens
1. Click on **Personal access tokens** in the left sidebar  
2. Select **Tokens (classic)**
3. Click **Generate new token** → **Generate new token (classic)**

**Direct URL**: [https://github.com/settings/tokens](https://github.com/settings/tokens)

### Step 4: Configure Your Token

#### For Fine-grained Tokens:
1. **Token name**: Give it a descriptive name (e.g., "PPMI Dashboard Development")
2. **Expiration**: Choose an expiration date (recommended: 90 days for security)
3. **Repository access**: Select which repositories this token can access
   - Select "Only select repositories" and choose `just4jc/ppmi-biomarker-dashboard`
4. **Permissions**: Choose the permissions you need:
   - **Contents**: Read and write (for cloning, pushing code)
   - **Metadata**: Read-only (automatically selected)
   - **Pull requests**: Read and write (if contributing via PRs)
   - **Issues**: Read and write (if managing issues)
   - **Releases**: Read and write (if managing data file releases)

#### For Classic Tokens:
1. **Note**: Give it a descriptive name (e.g., "PPMI Dashboard Development")
2. **Expiration**: Choose an expiration date (recommended: 90 days)
3. **Select scopes**: Check the boxes for permissions you need:
   - `repo` - Full control of private repositories (includes all sub-scopes)
   - `workflow` - Update GitHub Action workflows (if needed)
   - `write:packages` - Upload packages (if needed)
   - `delete:packages` - Delete packages (if needed)
   - `admin:org` - Full control of orgs and teams (only if managing organization)

### Step 5: Generate and Save Your Token

1. Click **Generate token** at the bottom of the page
2. **IMPORTANT**: Copy your token immediately and save it securely
   - You will **NOT** be able to see this token again
   - If you lose it, you'll need to generate a new one
3. Store it in a password manager or secure note

## How to Use Your Personal Access Token

### For Git Operations (HTTPS)

When cloning or pushing to a repository via HTTPS, use your token as the password:

```bash
# Clone a repository
git clone https://github.com/just4jc/ppmi-biomarker-dashboard.git
Username: your-github-username
Password: ghp_YourPersonalAccessTokenHere
```

### Store Token in Git Credential Manager (Recommended)

To avoid entering the token repeatedly:

#### On macOS:
```bash
git config --global credential.helper osxkeychain
```

#### On Windows:
```bash
git config --global credential.helper wincred
```

#### On Linux:
```bash
git config --global credential.helper cache
# Or for permanent storage:
git config --global credential.helper store
```

After setting up, the next time you clone/push, enter your token once and it will be cached.

### For GitHub CLI (`gh`)

```bash
# Authenticate with GitHub CLI
gh auth login

# Select: HTTPS
# Select: Paste an authentication token
# Paste your token
```

### For API Requests

```bash
# Using curl
curl -H "Authorization: token ghp_YourPersonalAccessTokenHere" \
     https://api.github.com/user
```

```python
# Using Python
import requests

headers = {
    "Authorization": "token ghp_YourPersonalAccessTokenHere"
}
response = requests.get("https://api.github.com/user", headers=headers)
```

## Security Best Practices

### ✅ DO:
- **Use fine-grained tokens** when possible (more secure, limited scope)
- **Set expiration dates** (90 days is a good balance)
- **Use minimum required permissions** (principle of least privilege)
- **Store tokens securely** in a password manager
- **Revoke unused tokens** regularly
- **Create separate tokens** for different purposes
- **Use secrets management** for tokens in CI/CD (e.g., GitHub Actions Secrets)

### ❌ DON'T:
- **Never commit tokens** to your repository (check `.gitignore`)
- **Don't share tokens** with others (create separate tokens for each person)
- **Don't use tokens in URLs** that might be logged
- **Don't give tokens more permissions** than needed
- **Don't use tokens without expiration** (security risk)
- **Don't hardcode tokens** in your scripts or applications

## Revoking a Token

If your token is compromised or no longer needed:

1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Find the token in your list
3. Click **Delete** or **Revoke**
4. Confirm the deletion

The token will be immediately invalidated.

## Troubleshooting

### "Authentication failed" Error

**Problem**: Git operations fail with authentication error

**Solution**:
1. Verify your token hasn't expired
2. Check that your token has the required permissions (`repo` scope for classic tokens)
3. Ensure you're using the token as the password, not your GitHub password
4. Clear cached credentials and try again:
   ```bash
   # macOS
   git credential-osxkeychain erase
   # Windows
   git credential-wincred erase
   # Linux
   git credential-cache exit
   ```

### "Resource not accessible" Error

**Problem**: API requests or Git operations fail with 404

**Solution**:
1. Check that the repository is accessible with your token's permissions
2. For private repositories, ensure your token has `repo` scope
3. Verify the repository URL is correct

### Token Not Showing in List

**Problem**: Can't find your token in settings

**Solution**:
1. Remember that tokens are only shown once during creation
2. If you lost your token, generate a new one
3. Revoke old tokens you're no longer using

## For This Repository (PPMI Dashboard)

### Cloning the Repository

Since this repository is now **public**, you can clone it without authentication:

```bash
git clone https://github.com/just4jc/ppmi-biomarker-dashboard.git
```

### Contributing Code

If you want to contribute:

1. **Fork the repository** (no token needed for forking)
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ppmi-biomarker-dashboard.git
   ```
3. **Create a branch**, make changes, and push to your fork
4. **Create a Pull Request** to the main repository

For pushing to your fork, you'll need a token if using HTTPS.

### Managing Releases (For Repository Maintainers)

To upload data files to GitHub Releases (as done for the biomarker data):

1. Generate a token with `repo` scope (classic) or appropriate release permissions (fine-grained)
2. Use the GitHub CLI:
   ```bash
   gh auth login
   # Then create/update releases
   gh release create v1.0.0 data-file.csv
   ```

## Additional Resources

- **GitHub Docs**: [Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- **GitHub CLI**: [GitHub CLI Manual](https://cli.github.com/manual/)
- **Token Scopes**: [Understanding scopes for OAuth apps](https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps)
- **Git Credential Storage**: [Git Credentials](https://git-scm.com/docs/git-credential-store)

## Summary

A GitHub Personal Access Token is a secure way to authenticate with GitHub for Git operations and API access. To locate or create one:

1. Go to **GitHub Settings** → **Developer settings** → **Personal access tokens**
2. **Generate a new token** with appropriate permissions
3. **Save it immediately** (you won't see it again!)
4. Use it as your **password** when Git asks for credentials

For questions specific to this PPMI Dashboard repository, please refer to the main [README.md](README.md) or create an issue.

---

**Last Updated**: December 2024  
**Repository**: just4jc/ppmi-biomarker-dashboard
