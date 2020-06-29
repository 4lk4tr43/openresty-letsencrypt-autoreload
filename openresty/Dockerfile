FROM openresty/openresty:alpine-fat

RUN apk update && apk upgrade
RUN apk add alpine-sdk inotify-tools luarocks python3
RUN luarocks install lua-resty-auto-ssl

RUN mkdir /src
RUN mkdir /configurations
RUN mkdir /content
RUN mkdir /etc/resty-auto-ssl
RUN mkdir /transformed

VOLUME /configurations
VOLUME /content
VOLUME /etc/resty-auto-ssl

RUN openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
    -subj '/CN=sni-support-required-for-valid-ssl' \
    -keyout /etc/ssl/resty-auto-ssl-fallback.key \
    -out /etc/ssl/resty-auto-ssl-fallback.crt

ADD src/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
ADD src/favicon.ico /usr/local/openresty/nginx/html/favicon.ico
ADD src/transform-configurations.py /src/transform-configurations.py
RUN chmod +x /src/transform-configurations.py
ADD src/start.sh /src/start.sh
RUN chmod +x /src/start.sh

ENTRYPOINT sh -c /src/start.sh
