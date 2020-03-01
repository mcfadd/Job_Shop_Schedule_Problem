#!/usr/bin/env bash

pip uninstall -y JSSP
cd ..
pip install .
cd docs
rm -rf _build
make buildapi
make html
pip uninstall -y JSSP
