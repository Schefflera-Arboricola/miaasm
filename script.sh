#!/bin/bash
set -m 
python3 build.py
python3 -m http.server 8000 --bind 127.0.0.1 --cgi -d _build &
sleep 3
open http://localhost:8000/ 
fg
