format-python-%:
	cd $* && autopep8 --in-place --recursive .

lint-python-%:
	cd $* && flake8 . --select=E9,F63,F7,F82 --show-source --statistics --exclude .venv
	cd $* && flake8 . --max-complexity=10 --max-line-length=127 --statistics --exclude .venv

test-python-%:
	cd $* && pytest

lint: lint-python-blank_server lint-python-chaos_proxy
	flake8 runserver.py --select=E9,F63,F7,F82 --show-source --statistics
	flake8 runserver.py --max-complexity=10 --max-line-length=127 --statistics

test: test-python-blank_server test-python-chaos_proxy

format: format-python-blank_server format-python-chaos_proxy
	autopep8 --in-place runserver.py
