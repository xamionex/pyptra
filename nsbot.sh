#!/bin/bash
cd ~/nsbot
while true; do
  python main.py
  echo "You have 2 seconds to stop the server using Ctrl-C. Server will restart otherwise"
  sleep 2
done;
