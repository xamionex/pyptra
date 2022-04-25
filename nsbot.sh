#!/bin/bash
cd ~/nsbot
while true; do
  python main.py
  echo "You have 5 seconds to stop the server using Ctrl-C. Server will restart otherwise"
  sleep 5
done;
