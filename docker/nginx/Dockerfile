FROM tutum/nginx
RUN rm /etc/nginx/sites-enabled/default
ADD docker/nginx/project /etc/nginx/sites-enabled/
ADD static /usr/src/app/static