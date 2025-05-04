#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/../"

current_branch=$(git symbolic-ref --short HEAD)
if [[ "$current_branch" != "master" ]]; then
    echo "❌ Releases can only happen from the 'master'. (Current: '$current_branch')"
    exit 1
fi

cd backup_to_harddrive/ && poetry version patch
VERSION_NUMBER=$(poetry version --short)
cd ../
./badges/create-badges.sh $VERSION_NUMBER

git commit -a -m release-"$VERSION_NUMBER"
git tag -a release-"$VERSION_NUMBER" -m "Release $VERSION_NUMBER"
git push origin release-"$VERSION_NUMBER"
