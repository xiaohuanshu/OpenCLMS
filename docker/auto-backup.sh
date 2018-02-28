#!/bin/sh
cd /root/backup
BACKUP_DATE=`date +%d-%m-%Y"_"%H_%M_%S`
docker exec -t checkinsystem_postgres_1 pg_dumpall -c -U postgres -f /tmp/dump_$BACKUP_DATE.dmp
docker cp checkinsystem_postgres_1:/tmp/dump_$BACKUP_DATE.dmp .
docker exec -t checkinsystem_postgres_1 rm -rf /tmp/dump_$BACKUP_DATE.dmp
/usr/local/bin/bypy upload
find . -mtime +6 -name "*.dmp" -exec rm -rf {} \;

cd /var/lib/docker/volumes/web_media/_data
/usr/local/bin/bypy -s 1T upload homeworkfile homeworkfile
/usr/local/bin/bypy -s 1T upload courseresource courseresource
/usr/local/bin/bypy -s 1T upload daily daily
exit