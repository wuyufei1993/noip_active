#!/bin/sh

cd google-chrome-stable
zip google-chrome-stable_current_amd64.zip  -s=0 --out google-chrome-stable.zip
unzip google-chrome-stable.zip
cd ../
docker build -t wuyufei1993/noipactive:latest .
cd google-chrome-stable
rm -rf google-chrome-stable.zip
rm -rf google-chrome-stable_current_amd64.deb
