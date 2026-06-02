# Team Project Template

> ⚠️ This is a placeholder. Replace this content with **project overview and setup instructions** when creating a new project.

This repository provides a standard starting point for projects developed by our team.  
While you may customise it to meet the needs of your project, the overall **repository structure must be maintained**.

```
│
├── .devcontainer/             # Development container definition 
│   └── devcontainer.json      # Development container config (e.g. tooling, features, extensions)
│
├── .github/                   # GitHub-specific configuration (e.g. Actions workflows, issue templates, PR templates)
│   └── pull_request_template.md         # Template for pull requests
│
├── config/                    # Global & environment-level configuration (e.g. repo-wide, environment or infrastructure YAML/JSON files)
│         
├── data/                      # Sample data, mock data or data schemas (full datasets ONLY when working locally)   
│   ├── processed/             # Cleaned or transformed data          
│   ├── raw/                   # Original, unprocessed data
│   │    └── raw-sample.csv    # Example placeholder file (at least one sample data, mock data or data schema must exist)
│   └── README.md              # Documents data source, owner, cloud storage details, etc.
│              
├── docker/                    # Docker-related assets for containerisation
│   ├── .dockerignore          # Excludes unnecessary files from Docker build context
│   └── Dockerfile             # Defines the Docker image build process (can be referenced in CI/CD)
│
├── docs/                      # Documentation *about* the project (e.g. usage guides, design notes, architecture diagrams)
│
├── infrastructure/            # Infrastructure-as-Code templates (e.g. Bicep, CloudFormation)
│   ├── aws/                   # AWS definition templates 
│   ├── azure/                 # Azure definition templates 
│   └── others/                # Cloud-agnostic definition templates
│
├── models/                    # Model-related code and files (e.g. architectures, training/eval/utils code, configs, docs and small test artifacts; large files in registry)
│   └── README.md              # Documents model purpose, registry links, usage, etc.
│ 
├── notebooks/                 # Jupyter notebooks for exploration, prototyping or analysis
│
├── pipelines/                 # CI/CD pipelines for Azure DevOps (ADO) 
│   ├── aws/                   # AWS deployment pipelines 
│   ├── azure/                 # Azure deployment pipelines 
│   └── others/                # Cloud-agnostic deployment pipelines 
│
├── reports/                   # Outputs produced *by* the project (e.g. generated analysis results, generated HTML/PDF reports) 
│   └── figures/               # Generated graphics and figures to be used in reporting (e.g. PNG/SVG plots, charts)
│
├── scripts/                   # Helper or automation scripts (e.g. Python or shell scripts, run directly or via Makefile)
│
├── src/                       # Core source code (e.g. modules, functions, classes)
│   └── app_config/            # Application code configuration (e.g. constants, runtime settings, app-specific defaults)
│
├── tests/                     # Automated test scripts (e.g. unit tests, integration tests, regression tests)
│
├── .env.sample                # Template for environment variables
├── .gitattributes             # Git configuration for file attributes (e.g. line endings, diff behavior, binary handling)
├── .gitignore                 # Specifies files/folders to ignore in version control 
├── CONTRIBUTING.md            # Guidelines for contributing to the project 
├── LICENSE                    # Licensing information for the project
├── Makefile                   # Defines automation commands (e.g. build, lint, test)
├── pyproject.toml             # Project metadata and Python dependencies (alternatively use requirements.txt for dependencies)
├── README.md                  # Project overview and setup instructions
├── SECURITY.md                # Security policies and vulnerability reporting
└── uv.lock                    # Locked dependency versions for reproducible environments
```

Refer to our team's [Repository Structure Standards](https://dev.azure.com/RioTintoDevOps/Analytics%20and%20Data%20Engineering%20Portfolio/_wiki/wikis/Analytics-and-Data-Engineering-Portfolio.wiki/15023/Repository-Structure-Standards) for detailed requirements.

## Setup Guides
Use the following guides to set up your repository:

1. [Development Environment (Dev Containers and uv)](https://dev.azure.com/RioTintoDevOps/Analytics%20and%20Data%20Engineering%20Portfolio/_wiki/wikis/Analytics-and-Data-Engineering-Portfolio.wiki/15034/How-to-Set-Up-Your-Development-Environment-(Dev-Containers-and-uv))
   - Use this guide to configure your development environment using dev containers and uv.

2. [Code Quality Tools](./docs/CODE_QUALITY_SETUP_GUIDE.md) 
   - Run these steps *inside your development container* to set up linting, formatting and other code-quality tools.

## Developer Guidelines
* [Current Guidelines](https://dev.azure.com/RioTintoDevOps/Analytics%20and%20Data%20Engineering%20Portfolio/_wiki/wikis/Analytics-and-Data-Engineering-Portfolio.wiki/11952/Current-Guidelines)
   * Ensure your project adheres to these standards and practices when developing and delivering digital solutions.


