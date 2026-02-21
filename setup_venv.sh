#!/bin/zsh
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
