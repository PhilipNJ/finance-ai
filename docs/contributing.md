# Contributing to Finance AI Dashboard

We welcome contributions to Finance AI Dashboard! This guide will help you get started.

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📖 Improve documentation
- 🧑‍💻 Submit code (PRs welcome!)
- ⭐ Star the repo

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/finance-ai.git
   cd finance-ai
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Run preflight check:
   ```bash
   poetry run python scripts/preflight_check.py
   ```

4. Launch the app:
   ```bash
   poetry run finance-ai
   ```

## Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the project's coding style

3. Test your changes:
   ```bash
   make test
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a Pull Request on GitHub

## Development Targets

The project uses Make for common development tasks:

- `make install` - Install dependencies
- `make run` - Run the application
- `make preflight` - Run preflight checks
- `make test` - Run tests
- `make export-reqs` - Export requirements.txt from Poetry

## Code Style

- Follow existing code patterns in the repository
- Write clear, descriptive commit messages
- Add comments for complex logic
- Update documentation for new features

## Adding New Agents

The agent system is extensible. Here's an example of creating a new agent:

```python
# In agents.py
class BudgetAgent:
    def __init__(self, llm_handler):
        self.llm = llm_handler
    
    def analyze_spending(self, month):
        # Use LLM to analyze spending patterns
        pass

# Add to workflow
workflow.budget_agent = BudgetAgent(llm)
```

## Documentation

Documentation is built using MkDocs with Material theme. To work on documentation:

### Local Testing

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material pymdown-extensions mkdocs-git-revision-date-localized-plugin

# Build and serve locally
mkdocs serve

# Or build static site
mkdocs build
```

The documentation will be available at http://127.0.0.1:8000/

### Documentation Structure

Documentation files are located in the `docs/` directory:

- `index.md` - Home page
- `getting-started.md` - Installation guide
- `quick-start.md` - Quick start tutorial
- `ai-architecture.md` - AI architecture overview
- `agent-workflow.md` - Agent workflow details
- `database-schema.md` - Database schema documentation
- `troubleshooting.md` - Troubleshooting guide
- `faq.md` - Frequently asked questions

## GitHub Actions Workflows

The repository uses GitHub Actions for continuous integration and deployment.

### Deploy MkDocs to GitHub Pages

**File**: `.github/workflows/deploy-docs.yml`

#### Purpose
Automatically builds and deploys the MkDocs documentation to GitHub Pages on every push to the `main` branch.

#### Workflow Details

- **Trigger**: Push to `main` branch
- **Deployment Target**: `gh-pages` branch
- **Python Version**: 3.11
- **Site URL**: https://philipnj.github.io/finance-ai

#### How It Works

1. **Checkout**: Fetches the full repository history (needed for git-revision-date plugin)
2. **Setup Python**: Installs Python 3.11
3. **Cache Dependencies**: Caches pip packages for faster subsequent runs
4. **Install Dependencies**: Installs MkDocs and required plugins
5. **Configure Git**: Sets up git credentials for the deployment commit
6. **Deploy**: Runs `mkdocs gh-deploy` to build and push to `gh-pages` branch

#### First-Time Setup

After merging a PR that adds workflows, GitHub Pages will automatically be configured. To verify:

1. Go to **Settings** → **Pages** in the GitHub repository
2. Confirm that **Source** is set to deploy from the `gh-pages` branch
3. The site should be live at: https://philipnj.github.io/finance-ai

#### Dependencies

The workflow installs the following packages:
- `mkdocs` - Static site generator
- `mkdocs-material` - Material theme for MkDocs
- `pymdown-extensions` - Markdown extensions
- `mkdocs-git-revision-date-localized-plugin` - Shows last updated dates

These are also defined in `pyproject.toml` under `[tool.poetry.group.dev.dependencies]`.

#### Troubleshooting Workflows

If the deployment fails:

1. Check the **Actions** tab in GitHub to see the workflow logs
2. Verify that the `gh-pages` branch exists and has the correct permissions
3. Ensure that GitHub Pages is enabled in repository settings
4. Check that there are no YAML syntax errors in `mkdocs.yml`

#### Manual Deployment

If needed, you can trigger a manual deployment:

1. Go to the **Actions** tab
2. Select the "Deploy MkDocs to GitHub Pages" workflow
3. Click "Run workflow" → select `main` branch → "Run workflow"

Or push an empty commit to trigger the workflow:

```bash
git commit --allow-empty -m "Trigger docs deployment"
git push origin main
```

Or deploy manually (requires write access):

```bash
mkdocs gh-deploy --force --clean --verbose
```

## Getting Help

- 📖 Read the [Documentation](index.md)
- 🐛 Check [Troubleshooting Guide](troubleshooting.md)
- 💬 Ask in GitHub Discussions
- 🐛 Open an issue on GitHub

## License

By contributing to Finance AI Dashboard, you agree that your contributions will be licensed under the MIT License.
