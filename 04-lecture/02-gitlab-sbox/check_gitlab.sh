#!/bin/bash

while true; do curl -s --connect-timeout 5 https://gitlab.__SLURM_USERNAME__.edu.slurm.io -LI | grep '200' 2>&1 > /dev/null; if [ $? -eq 0 ]; then echo OK; else echo FAIL; fi; sleep 5; done
