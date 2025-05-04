# Contributing

It is recommended VSCode IDE with the *Reopen in container feature*
(devcontainer)

## Developer how to

### Basics

- Clean the repository: `git clean -e ".vscode/*" -fxfd`
- Install package dependencies: use the **Install dependencies** task of VSCode
- Run unittest: use the **Unit-tests** task of VSCode.
You can check code coverage in `output/coverage_report/index.html`
- Run pylint on the repository: use the **Pylint check** task of VSCode.
- Format everything in the repository: use the **Format everything** task of VSCode.
- Use GUI for testing: `Ctrl+Shift+P` *"Python: Select Interpreter"*,
use the one from `.cache/pypoetry/...`
- Build a wheel package: use the **Build package** task of VSCode.
- Create a new release: from branch `master` execute `./processes/create_new_release.sh`

### Advanced

- Run all tests associated to a given usecase: run **Validate use case**
task of VSCode and input the correct test list file
(e.g. `usecase_6_test_list.txt`)
