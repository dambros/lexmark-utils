#!/bin/bash

pipenv run python ./file_merger.py merge
pipenv run python ./index_verifier.py check