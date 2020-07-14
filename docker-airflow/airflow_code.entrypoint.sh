#!/bin/sh

# Copy application assets to the shared directory

echo "Deleting old files"
rm /root/deploy/*
rm -rf /root/deploy/**/*
echo "Finish delete old files"

mkdir -p /root/deploy

echo "Coping new files"
cp -a /root/airflow/* /root/deploy
echo "Finish copy new files"


echo "FINISH!!!  signal healthy"
touch /root/airflow/done.txt


# Run the CMD as the main container process
exec "$@"
