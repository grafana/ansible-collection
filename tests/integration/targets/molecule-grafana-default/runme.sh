#!/usr/bin/env bash

version="0.1.4"
src="https://github.com/gardar/ansible-test-molecule/releases/download/$version/ansible-test-molecule.sh"

# shellcheck disable=SC1090
if [[ -v GITHUB_TOKEN ]]
then
  source <(curl -L -s -H "Authorization: token $GITHUB_TOKEN" $src)
else
  source <(curl -L -s $src)
fi
