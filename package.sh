
pip install --target ./package inflection

cd package
zip -r ../deployment.zip .

cd ..
zip deployment.zip LFs/lf6-produce-match.py
