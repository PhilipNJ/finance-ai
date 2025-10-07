# GitHub Actions Workflows

This directory contains automated workflows for the Finance AI Dashboard repository.

## Deploy MkDocs to GitHub Pages

**File**: `workflows/deploy-docs.yml`

### Purpose
Automatically builds and deploys the MkDocs documentation to GitHub Pages on every push to the `main` branch.

### Workflow Details

- **Trigger**: Push to `main` branch
- **Deployment Target**: `gh-pages` branch
- **Python Version**: 3.11
- **Site URL**: https://philipnj.github.io/finance-ai

### How It Works

1. **Checkout**: Fetches the full repository history (needed for git-revision-date plugin)
2. **Setup Python**: Installs Python 3.11
3. **Cache Dependencies**: Caches pip packages for faster subsequent runs
4. **Install Dependencies**: Installs MkDocs and required plugins
5. **Configure Git**: Sets up git credentials for the deployment commit
6. **Deploy**: Runs `mkdocs gh-deploy` to build and push to `gh-pages` branch

### First-Time Setup

After merging this PR, GitHub Pages will automatically be configured. To verify:

1. Go to **Settings** → **Pages** in the GitHub repository
2. Confirm that **Source** is set to deploy from the `gh-pages` branch
3. The site should be live at: https://philipnj.github.io/finance-ai

### Local Testing

To test the documentation build locally:

```bash
# Install dependencies
pip install mkdocs mkdocs-material pymdown-extensions mkdocs-git-revision-date-localized-plugin

# Build and serve locally
mkdocs serve

# Or build static site
mkdocs build

# Or deploy manually (requires write access)
mkdocs gh-deploy --force --clean --verbose
```

### Dependencies

The workflow installs the following packages:
- `mkdocs` - Static site generator
- `mkdocs-material` - Material theme for MkDocs
- `pymdown-extensions` - Markdown extensions
- `mkdocs-git-revision-date-localized-plugin` - Shows last updated dates

These are also defined in `pyproject.toml` under `[tool.poetry.group.dev.dependencies]`.

### Troubleshooting

If the deployment fails:

1. Check the **Actions** tab in GitHub to see the workflow logs
2. Verify that the `gh-pages` branch exists and has the correct permissions
3. Ensure that GitHub Pages is enabled in repository settings
4. Check that there are no YAML syntax errors in `mkdocs.yml`

### Manual Deployment

If needed, you can trigger a manual deployment:

1. Go to the **Actions** tab
2. Select the "Deploy MkDocs to GitHub Pages" workflow
3. Click "Run workflow" → select `main` branch → "Run workflow"

Or push an empty commit to trigger the workflow:

```bash
git commit --allow-empty -m "Trigger docs deployment"
git push origin main
```
