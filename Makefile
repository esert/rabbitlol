.PHONY: setup run test unit-coverage e2e-coverage coverage deploy clean python

setup:
	virtualenv-2.7 . && \
	source bin/activate && \
	pip install \
	coverage \
	flask \
	mock \
	nose-exclude \
	nosegae \
	oauth2 \
	pytest \
	pyyaml
	ls app/secrets.py || cp app/secrets.py_TEMPLATE app/secrets.py

run: setup
	dev_appserver.py .

test:
	nosetests --logging-level=ERROR --with-gae

unit-coverage:
	make EXCLUDE=app/tests/e2e coverage

e2e-coverage:
	make EXCLUDE=app/tests/unit coverage

coverage:
	rm -f .coverage && \
	nosetests \
	--exclude-dir=${EXCLUDE} \
	--logging-level=ERROR \
	--with-gae \
	--with-coverage \
	--cover-package=app \
	--cover-branches \
	--cover-erase \
	--cover-html && \
	echo "Report: file://`pwd`/cover/index.html"

# Run this as PROJECT_ID=<your-project-id> make deploy
deploy: setup test
	appcfg.py -A ${PROJECT_ID} -V dev update .

clean:
	rm -rf bin/ lib/ cover/ man/ include && find . -name '*.pyc' | xargs -n 1 rm

# Start a python shell where you can import app module. Assumes App
# Engine related python files are in /usr/local
python:
	PYTHONPATH=/usr/local/google_appengine python
