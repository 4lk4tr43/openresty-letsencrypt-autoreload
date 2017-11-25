FROM openresty/openresty:xenial

RUN apt update && apt install -y inotify-tools python3
RUN luarocks install lua-resty-auto-ssl

RUN mkdir /src
RUN mkdir /configurations
RUN mkdir /content
RUN mkdir /etc/resty-auto-ssl
RUN mkdir /transformed

ADD src/nginx.conf /usr/local/openresty/nginx/conf/
ADD src/favicon.ico /usr/local/openresty/nginx/html/
ADD src/start.sh /src/
ADD src/transform-configurations.py /src/
ADD src/requirements.txt /src/

RUN chmod +x /src/start.sh
RUN chmod +x /src/transform-configurations.py

RUN openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
    -subj '/CN=sni-support-required-for-valid-ssl' \
    -keyout /etc/ssl/resty-auto-ssl-fallback.key \
    -out /etc/ssl/resty-auto-ssl-fallback.crt

VOLUME /configurations
VOLUME /content
VOLUME /etc/resty-auto-ssl

ENTRYPOINT /src/start.sh

