format-python-%:
	cd $* && autopep8 --in-place --recursive .

lint-python-%:
	cd $* && flake8 . --select=E9,F63,F7,F82 --show-source --statistics --exclude .venv
	cd $* && flake8 . --max-complexity=10 --max-line-length=127 --statistics --exclude .venv

lint: lint-python-blank-server lint-python-chaos-proxy

test-python-%:
	cd $* && pytest

test: test-python-blank-server test-python-chaos-proxy

format: format-python-blank-server format-python-chaos-proxy
