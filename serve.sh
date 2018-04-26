#!/usr/bin/env bash

echo $PASS | sudo -S service mongod start
sleep 10 # give mongodb some more time to start listening
python serve.py --prod --port 6785

