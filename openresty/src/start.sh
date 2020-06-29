python3 /src/transform-configurations.py
openresty

while true; do
    inotifywait -r -e modify,attrib,move_self /configurations/
    /src/transform-configurations.py
    openresty -s reload
done