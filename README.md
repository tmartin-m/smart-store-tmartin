# Pro Analytics 02 Python Starter Repository

> Use this repo to start a professional Python project.

- Additional information: <https://github.com/denisecase/pro-analytics-02
- Project organization: [STRUCTURE](./STRUCTURE.md)
- Build professional skills:
  - **Environment Management**: Every project in isolation
  - **Code Quality**: Automated checks for fewer bugs
  - **Documentation**: Use modern project documentation tools
  - **Testing**: Prove your code works
  - **Version Control**: Collaborate professionally

---

## Module 1 - BI Python (Get Started, add Raw Data)

Goals:
1. Set up a machine for professional BI work.
2. Set up a project (a repository) that we will use over time
3. Use the daily workflow to update our copy of the template and add some raw data files.

[Drivers](https://github.com/denisecase/smart-sales-analysis-goals)

[Basic Files and Folders](https://github.com/denisecase/applied-computer-organization)

<details>
<summary>Click to see Pre-Commit note</summary>

1. Open pyproject.toml
2. Add the pre-commit line below.
3. Save the File
4. Run the commands below.

```shell
[project.optional-dependencies]
dev = [
  "pre-commit", # code quality checks before commits
  "pytest", # run some tests automatically
  "pytest-cov", # coverage report for more visibility
]
docs = [
  "mkdocs",                # Core MkDocs
  "mkdocs-material",       # Modern, responsive theme
  "mkdocstrings[python]",  # Auto-generate API docs from docstrings
  "livereload",            # Enables live reload (auto-refresh on edit)
  "watchdog",              # Faster and more reliable file watching
  "ruff",                  # Needed so mkdocstrings can format signatures
]
```
```shell
uv sync --extra dev --extra docs --upgrade
```
```shell
uv run pre-commit install
```
</details>

Follow the Workflows below.

---

## WORKFLOW 1. Set Up Your Machine

Proper setup is critical.
Complete each step in the following guide and verify carefully.

- [SET UP MACHINE](./SET_UP_MACHINE.md)

---

## WORKFLOW 2. Set Up Your Project

After verifying your machine is set up, set up a new Python project by copying this template.
Complete each step in the following guide.

- [SET UP PROJECT](./SET_UP_PROJECT.md)

It includes the critical commands to set up your local environment (and activate it):

```shell
uv venv
uv python pin 3.12
uv sync --extra dev --extra docs --upgrade
uv run pre-commit install
uv run python --version
```

**Windows (PowerShell):**

```shell
.\.venv\Scripts\activate
```
---

## WORKFLOW 3. Daily Workflow

Please ensure that the prior steps have been verified before continuing.
When working on a project, we open just that project in VS Code.

### 3.1 Git Pull from GitHub

Always start with `git pull` to check for any changes made to the GitHub repo.

```shell
git pull
```

### 3.2 Run Checks as You Work

This mirrors real work where we typically:

1. Update dependencies (for security and compatibility).
2. Clean unused cached packages to free space.
3. Use `git add .` to stage all changes.
4. Run ruff and fix minor issues.
5. Update pre-commit periodically.
6. Run pre-commit quality checks on all code files (**twice if needed**, the first pass may fix things).
7. Run tests.

In VS Code, open your repository, then open a terminal (Terminal / New Terminal) and run the following commands one at a time to check the code.

```shell
uv sync --extra dev --extra docs --upgrade
uv cache clean
git add .
uvx ruff check --fix
uvx pre-commit autoupdate
uv run pre-commit run --all-files
git add .
uv run pytest
```

NOTE: The second `git add .` ensures any automatic fixes made by Ruff or pre-commit are included before testing or committing.

<details>
<summary>Click to see a note on best practices</summary>

`uvx` runs the latest version of a tool in an isolated cache, outside the virtual environment.
This keeps the project light and simple, but behavior can change when the tool updates.
For fully reproducible results, or when you need to use the local `.venv`, use `uv run` instead.

</details>

### 3.3 Build Project Documentation

Make sure you have current doc dependencies, then build your docs, fix any errors, and serve them locally to test.

```shell
uv run mkdocs build --strict
uv run mkdocs serve
```

- After running the serve command, the local URL of the docs will be provided. To open the site, press **CTRL and click** the provided link (at the same time) to view the documentation. On a Mac, use **CMD and click**.
- Press **CTRL c** (at the same time) to stop the hosting process.

### 3.4 Execute

This project includes demo code.
Run the demo Python modules to confirm everything is working.

In VS Code terminal, run:

```shell
uv run python -m analytics_project.demo_module_basics
uv run python -m analytics_project.demo_module_languages
uv run python -m analytics_project.demo_module_stats
uv run python -m analytics_project.demo_module_viz
```

You should see:

- Log messages in the terminal
- Greetings in several languages
- Simple statistics
- A chart window open (close the chart window to continue).

If this works, your project is ready! If not, check:

- Are you in the right folder? (All terminal commands are to be run from the root project folder.)
- Did you run the full `uv sync --extra dev --extra docs --upgrade` command?
- Are there any error messages? (ask for help with the exact error)

---

### 3.5 Git add-commit-push to GitHub

Anytime we make working changes to code is a good time to git add-commit-push to GitHub.

1. Stage your changes with git add.
2. Commit your changes with a useful message in quotes.
3. Push your work to GitHub.

```shell
git add .
git commit -m "describe your change in quotes"
git push -u origin main
```

This will trigger the GitHub Actions workflow and publish your documentation via GitHub Pages.

### 3.6 Modify and Debug

With a working version safe in GitHub, start making changes to the code.

Before starting a new session, remember to do a `git pull` and keep your tools updated.

Each time forward progress is made, remember to git add-commit-push.

---

## Module 2 - BI Python - reading raw data into panda DataFrames

Goals:
1. Create a new file: src/analytics_project/data_prep.py
   1. [P2-data_prep.py](https://github.com/denisecase/smart-sales-starter-files/blob/main/src/analytics_project/data_prep.py)
2. Start with at docstring at the top.
3. Make a place for imports after the docstring.
4. Set up global constants (we'll use these for our project paths).
5. Make a place for defining the reusable function.
6. After the reusable function(s), define a function named main() to hold the initial logic for our processing pipeline.
7. Use the standard Python conditional execution block to run the main() method when we execute this module directly.

Execute:
```shell
uv run python -m analytics_project.data_prep
```

Log Proof:
- 2025-10-30 19:08:INFO    AT data_prep.py:32: Reading raw data from C:\Repos\smart-store-tmartin\data\raw\customers_data.csv.
- 2025-10-30 19:08:INFO    AT data_prep.py:35: customers_data.csv: loaded DataFrame with shape 201 rows x 4 cols
- 2025-10-30 19:08:INFO    AT data_prep.py:32: Reading raw data from C:\Repos\smart-store-tmartin\data\raw\products_data.csv.
- 2025-10-30 19:08:INFO    AT data_prep.py:35: products_data.csv: loaded DataFrame with shape 100 rows x 4 cols
- 2025-10-30 19:08:INFO    AT data_prep.py:32: Reading raw data from C:\Repos\smart-store-tmartin\data\raw\sales_data.csv.
- 2025-10-30 19:08:INFO    AT data_prep.py:35: sales_data.csv: loaded DataFrame with shape 2001 rows x 7 cols

## Module 3 - Prepare Data for ETL

Goals:
1. Employ Python pandas to perform some common cleaning and prep tasks.
   1. [Data Cleaning Process](https://github.com/denisecase/smart-sales-docs/blob/main/D33_Data_Cleaning_with_pandas.md)
2. Wrap this functionality into a reusable DataScrubber class.
   1. [Reference File](https://github.com/denisecase/smart-sales-docs/blob/main/utils/data_scrubber.py)
3. Use Python unittest (from the Python Standard Library) to verify the DataScrubber class methods have been correctly defined and perform the necessary logic correctly.
4. Finish the TODO items in the provided DataScrubber class.
5. Run the test data scrubber script to verify ALL tests pass 100%.
6. Use the DataScrubber class in your data prep script.

<details>
<summary>Click to see a note on pathway errors</summary>

smart-store-tmartin/
└── src/
    └── analytics_project/
        ├── scripts/
        │   └── data_preparation/
        │       └── prepare_customers.py
        ├── utils/
        │   ├── __init__.py
        │   ├── logger.py
        │   └── data_scrubber.py

</details>
