#!/bin/bash

/usr/local/openresty/bin/openresty

while true; do
    inotifywait -r -e modify,attrib,move_self /configurations/
    /src/transform-configurations.py
    /usr/local/openresty/bin/openresty -s reload
done