FROM openresty/openresty:xenial

RUN apt update && apt install -y inotify-tools python
RUN luarocks install lua-resty-auto-ssl

ADD src/nginx.conf /usr/local/openresty/nginx/conf/
ADD src/start.sh /
ADD src/favicon.ico /usr/local/openresty/nginx/html/

RUN mkdir /configurations
RUN mkdir /content
RUN mkdir /etc/resty-auto-ssl
RUN chmod +x start.sh
RUN chown nobody /etc/resty-auto-ssl
RUN openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
    -subj '/CN=sni-support-required-for-valid-ssl' \
    -keyout /etc/ssl/resty-auto-ssl-fallback.key \
    -out /etc/ssl/resty-auto-ssl-fallback.crt

VOLUME /configurations
VOLUME /content
VOLUME /etc/resty-auto-ssl

ENTRYPOINT ./start.sh

