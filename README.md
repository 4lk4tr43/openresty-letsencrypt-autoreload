1. clone this repository
2. docker-compose build
3. docker stack deploy -c docker-compose.yml [stack-name] or docker-compose up
4. add conf file to the mnt/configurations/ folder

(NOTE: does not block any domain or ip address from creating certificates)

```
# only files with .conf extension are loaded and transformed
# to load configurations without transforming use the .nginx extension

# ssl example
# ssl_certificate_by_lua_block { auto_ssl:ssl_certificate() }
# lua letsencrypt is added if missing and no certificates are specified, it's added to the beginning of the server block
# ssl_certificate /etc/ssl/resty-auto-ssl-fallback.crt;
# ssl_certificate_key /etc/ssl/resty-auto-ssl-fallback.key;
# fallback certificates are added to the end of the server block if no certificates were specified
server {
    listen       443 http2 ssl;
    server_name  example.com;

    location / {
        root   /content; # this is a mounted volume

        header_filter_by_lua_block {
            ngx.header["server"] = nil
        }
        index  index.html index.htm;
        gzip   on;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   html;
    }
}

# http example
# location /.well-known/acme-challenge/ { content_by_lua_block { auto_ssl:challenge_server() } }
# is added to the server block to the beginning of the server block
server {
    listen       80;
    server_name  example.com;

    location / {
        root   /content;
        index  index.html index.htm;
        gzip   on;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   html;
    }
}
```

##### NOTE for Qnap users
To open port 80 stop the Apache service `/etc/init.d/Qthttpd.sh stop`