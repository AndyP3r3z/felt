#!/usr/bin/env bash
#
# Date:    2026/02/16
# Author:  andyp3r3z
#
# Installation script.

repo="git+https://github.com/AndyP3r3z/felt.git"

uv_install(){
	uv tool install "$repo"
}

pip_install(){
	# Create virtual env.
	python -m venv .felt
	# activate it
	source .felt/bin/activate
	# install
	pip install "$repo"
}

uv_install
