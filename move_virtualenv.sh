#!/bin/bash

[[ $(uname) == "Darwin" ]] || { echo "This script only runs on Mac!"; exit -1; }

[[ $# == 3 ]] || { echo "$0 <virtualenv> <src_python_version> <dst_python_version>"; exit -1; }

venv=$1
src=$2
dst=$3

# Sanity Checks
[[ $(basename $(pyenv prefix)) == $dst ]] || { echo "we are not in target version $dst!"; exit -1; }
[[ -d $(pyenv root)/versions/$src/envs/$venv ]] || { echo "virtualenv '$venv' needs to be in $src!"; exit -1; }
[[ "$(readlink $(pyenv root)/versions/$venv)" == "$(pyenv root)/versions/$src/envs/$venv" ]] || \
    { echo virtualenv $venv needs to point to $src/envs/$venv; exit -1; }
[[ ! -e $(pyenv root)/versions/$dst/$venv ]] || { echo "virtual env '$venv' exists in $dst!"; exit -1; }

set -x

mkdir -p $(pyenv root)/versions/$dst/envs/
mv $(pyenv root)/versions/$src/envs/$venv $(pyenv root)/versions/$dst/envs/

cd $(pyenv root)/versions/$dst/envs/$venv/bin

# replace all python version in bin/
ls -1 | xargs -I{} file {} | grep text | sed -ne 's/\(.*\):\(.*\)$/\1/p' | xargs -I{} echo sed -i -e "s/$src/$dst/" {}
# and pyvenv.cfg
pyvenv_cfg=$(pyenv root)/versions/$dst/envs/$venv/pyvenv.cfg
[[ -f $pyvenv_cfg ]] && sed -i -e "s/$src/$dst/" $pyvenv_cfg
# replace python with target version.
ln -sf $(pyenv root)/versions/$dst/bin/python3.5

cd - &>/dev/null

ln -sf $(pyenv root)/versions/$dst/envs/$venv $(pyenv root)/versions/$venv
pyenv versions | grep $venv
