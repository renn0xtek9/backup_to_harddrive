# Readme

This is a template of repository for developing python packages using poetry with
VSCode as IDE using the .devcontainer feature.
Utilities like pylint, black etc. pre-installed to help developer get going.

When you want to start a new project you have two options:

1. Template repository feature:
Simply use the template repository feature of github.
[See also](https://docs.github.com/de/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
2. Manually:
    Just pull this git repository, then
    remove the git reposotiory using:

    ```bash
    rm -rf .git
    ```

    Then, recreate a new git repository

    ```bash
    git init
    ```

Add all files and then push the repository to your github project.

**In both cases!:**

- Don't forget to change all occurrence"package_foobar" name by the name you want
for you python package. (Use the Ctrl+Shift+R feature of VSCode to make sure you
won't forget any occurrence).
- Don't forget to adapt
  - [LICENSE](package_foobar/LICENSE)
  - [pyproject.toml](package_foobar/pyproject.toml)
