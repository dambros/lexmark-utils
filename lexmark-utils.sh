#!/bin/bash

cd /opt/sistemas/dataeasy/lexmark-utils-master && /home/lexmark/.local/bin/pipenv run python file_merger.py merge -c /usr/bin/convert
cd /opt/sistemas/dataeasy/lexmark-utils-master && /home/lexmark/.local/bin/pipenv run python index_verifier.py check
