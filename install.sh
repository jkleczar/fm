#!/bin/bash

CWD=$(pwd)
echo 'alias fml="python '$CWD'/fml.py"' >> $HOME/.bashrc
echo 'export FMLRC='$CWD'/.fmlrc' >> $HOME/.bashrc

