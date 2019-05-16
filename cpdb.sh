#!/bin/sh
                               
set -ex

DB='ateliersoude'                    
SSH_HOST='hbhttp2'             
REMOTE_MEDIA='/srv/app/ateliersoude/media/'

dropdb $DB
createdb $DB
ssh $SSH_HOST pg_dump --no-owner --no-privileges $DB | psql $DB

rsync -avz -e ssh --delete $SSH_HOST:$REMOTE_MEDIA media/

