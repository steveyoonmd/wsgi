#!/builds/sh

rm -rf ./builds
mkdir -p ./builds/package

rm -rf ./base/__pycache__
rm -rf ./libs/__pycache__
rm -rf ./models/__pycache__
rm -rf ./routes/__pycache__

cp -r ./base ./builds
cp -r ./libs ./builds
cp -r ./models ./builds
cp -r ./routes ./builds
cp -r ./static ./builds
cp cfg.json ./builds
cp lambda_function.py ./builds

cd ./builds
# pip3 install --target ./package 'pymysql[rsa]'
pip3 install --target ./package pymysql
pip3 install --target ./package pycrypto

DATE=$(date '+%Y%m%d_%H%M%S_%Z')

cd ./package
zip -r9 ${OLDPWD}/build_$DATE.zip .

cd $OLDPWD
zip -r9 ./build_$DATE.zip ./blueprints
zip -r9 ./build_$DATE.zip ./libs
zip -r9 ./build_$DATE.zip ./static

zip -g build_$DATE.zip cfg.json
zip -g build_$DATE.zip lambda_function.py

# aws lambda update-function-code --function-name my-function --zip-file fileb://build_$DATE.zip
