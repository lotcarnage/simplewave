rm -rf dist
python setup.py sdist --format=zip
twine upload --repository pypitest ./dist/*
