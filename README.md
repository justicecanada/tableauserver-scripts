# Tableau Workbook Export Tool

A collection of Python scripts to:

1. Export workbooks from a Tableau server while preserving the project hierarchy structure.
2. Generate client reports

## Prerequisites

- Python 3.6 or higher
- Access to a Tableau server
  - Administrator permissions to download workbooks

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

- [Export Workbooks](Backups/README.md)
- [Generate Client Reports](ClientReports/README.md)

## Contributing

- Don't push commits directly to `main`.
- Always branch off `main` to create a feature branch, e.g. `git checkout -b update-readme`
- Give your PR a descriptive title using [conventional commits](https://kapeli.com/cheat_sheets/Conventional_Commits.docset/Contents/Resources/Documents/index), e.g.:
  - `fix: pdf not being exported` for a bug fix
  - `feat: new datasource extraction script` for a new feature
  - `chore: upgrade library version`
  - `refactor: rename function`
- To indicate that the PR *isn't* ready to merge, create a `Draft PR`
- Get someone else to review your PR before merging it.

After your PR is merged:

- On your workstation, `git checkout main` and `git pull`
- Delete the branch that was just merged, e.g. `git branch -D update-readme`
- Create a new feature branch, if you are ready to do so.
