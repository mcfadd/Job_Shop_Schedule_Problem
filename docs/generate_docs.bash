#!/usr/bin/env bash

echo 'y' | pip uninstall JSSP
cd ..
pip install .
cd docs
rm -rf _build
rm -rf doc
sphinx-apidoc -o doc ../JSSP
make html
