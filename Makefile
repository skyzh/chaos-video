format-python-%:
	cd $* && autopep8 --in-place --recursive .

lint-python-%:
	cd $* && flake8 . --select=E9,F63,F7,F82 --show-source --statistics --exclude .venv
	cd $* && flake8 . --max-line-length=127 --ignore=E722,W503,W504 --statistics --exclude .venv

test-python-%:
	cd $* && pytest

format-nodejs-%:
	cd $* && ./node_modules/.bin/prettier --write "src/**/*.{js,jsx,ts,tsx,json,css,scss,md}" -w

lint-nodejs-%:
	cd $* && ./node_modules/.bin/prettier --write "src/**/*.{js,jsx,ts,tsx,json,css,scss,md}" -c

lint: lint-python-blank_server lint-python-chaos_proxy lint-python-video-gen

test: test-python-blank_server test-python-chaos_proxy

format: format-python-blank_server format-python-chaos_proxy format-python-video-gen
