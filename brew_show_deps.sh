#!/bin/zsh

# http://zanshin.net/2014/02/03/how-to-list-brew-dependencies/

brew list | while read cask; do echo -n $fg[blue] $cask $fg[white]; brew deps $cask | awk '{printf(" %s ", $0)}'; echo ""; done
