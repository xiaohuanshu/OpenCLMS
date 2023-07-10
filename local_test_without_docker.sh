#!/bin/sh

# run server with .env configured & without docker

cd "$(dirname $0)"
sh -c 'export $(cat .env |sed "/^#/d" |xargs); ./manage.py runserver'
