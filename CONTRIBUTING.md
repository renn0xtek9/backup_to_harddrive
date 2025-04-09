# Contributing

It is recommended to the *Reopen in container feature*

## Developer how to

- Clean the repository: `git clean -e ".vscode/*" -fxfd`
- Install package dependencies: **Install dependencies** task of VSCode
- Run unittest: use the **Unit-tests** task of VSCode.
You can check code coverage in `output/coverage_report/index.html`
- Run pylint on the repository: use the **Pylint check** task of VSCode.
- Format everything in the repository: use the **Format everything** task of VSCode.
- Use GUI for testing: `Ctrl+Shift+P` *"Python: Select Interpreter"*,
use the one from `.cache/pypoetry/...`
- Build a wheel package: use the **Build package** task of VSCode.
- Create a new release:
  - `cd backup_to_harddrive/ && poetry version patch`
  - note the new version number in [pyproject.toml](backup_to_harddrive/pyproject.toml#L7)
  (e.g. X.Y.Z)
  - `git tag -a release-X.Y.Z`
  - `git push origin release-X.Y.Z`
