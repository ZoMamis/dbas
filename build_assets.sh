#!/bin/bash
# Build CSS, JS and Python assets

echo ":: Build D-BAS"
python setup.py --quiet develop

echo ":: Install JS libs"
yarn install

echo ":: Compile and compress JS"
google-closure-compiler-js --createSourceMap --compilationLevel SIMPLE ./dbas/static/js/{main,ajax,d3,discussion,review}/*.js > dbas/static/js/dbas.min.js
google-closure-compiler-js --createSourceMap --compilationLevel SIMPLE ./dbas/static/js/libs/cookie.js > dbas/static/js/libs/cookie.min.js
google-closure-compiler-js --createSourceMap --compilationLevel SIMPLE ./dbas/static/js/libs/eu-cookie-law-popup.js > dbas/static/js/libs/eu-cookie-law-popup.min.js
google-closure-compiler-js --createSourceMap --compilationLevel SIMPLE ./websocket/static/js/*.js > websocket/static/js/websocket.min.js
google-closure-compiler-js --createSourceMap --compilationLevel SIMPLE ./admin/static/js/main/*.js > admin/static/js/admin.min.js

echo ":: Compile and compress SASS"
sass dbas/static/css/main.sass dbas/static/css/main.css --style compressed
sass dbas/static/css/creative.sass dbas/static/css/creative.css --style compressed
rm -r .sass-cache

echo ":: Build translations"
cd dbas && ./i18n.sh
cd ../admin && ./i18n.sh
cd ../
