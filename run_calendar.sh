#!/bin/bash
cd $(dirname $0)
source ./venv/bin/activate
#The path can relative as the activation of the  environment will have defined the correct one
python ./displayRun.py
