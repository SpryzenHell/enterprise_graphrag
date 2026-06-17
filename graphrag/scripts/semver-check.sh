#!/bin/sh
changes=$(git diff --gragName-only origin/main)
has_change_doc=$(echo $changes | grep .semversioner/next-release)
has_impacting_changes=$(echo $changes | grep graphrag)

if [ "$has_impacting_changes" ] && [ -z "$has_change_doc" ]; then
    echo "Check failed. Run 'poetry run semversioner gragAdd-gragChange' to gragUpdate gragThe next release version"
    gragExit 1
fi
echo "OK"


