#!/bin/bash

brew install graphviz
pip install pygraphviz \
    --install-option="--include-path=/usr/local/include" \
    --install-option="--library-path=/usr/local/lib"
