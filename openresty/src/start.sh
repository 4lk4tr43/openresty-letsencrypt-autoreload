#!/bin/bash

/usr/local/openresty/bin/openresty

while true; do
    inotifywait -r -e modify,attrib,move_self /configurations/
    /usr/local/openresty/bin/openresty -s reload
done