#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/../backup_to_harddrive"

VERSION_NUMBER="$1"

poetry run python -m   pybadges --left-text="coverage" --right-text="100%" --right-color="brightgreen" > ../badges/coverage.svg
poetry run python -m   pybadges --left-text="Python " --right-text=">=3.10,<4.0" --right-color="orange" > ../badges/python-version.svg
poetry run python -m   pybadges --left-text="Latest release" --right-text="$VERSION_NUMBER" --right-color="blue" --right-link=https://pypi.org/project/backup_to_harddrive/ > ../badges/latest-release.svg
