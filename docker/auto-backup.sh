#!/bin/sh
cd /root/backup
docker exec -t checkinsystem_postgres_1 pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.dmp
/usr/local/bin/bypy upload
find . -mtime +6 -name "*.dmp" -exec rm -rf {} \;

cd /var/lib/docker/volumes/web_media/_data
/usr/local/bin/bypy upload
exit