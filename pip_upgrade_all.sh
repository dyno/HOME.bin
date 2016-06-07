#!/bin/bash

set -x

# http://stackoverflow.com/questions/2720014/upgrading-all-packages-with-pip
# https://github.com/pypa/pip/issues/59

# pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

pip list --outdated | awk '{print $1;}' | xargs -I{} pip install -U {}
