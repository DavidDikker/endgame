SHELL:=/bin/bash

.PHONY: setup-env
setup-env:
	python3 -m venv ./venv && source venv/bin/activate
	python3 -m pip install -r requirements.txt

.PHONY: setup-dev
setup-dev: setup-env
	python3 -m pip install -r requirements-dev.txt

.PHONY: build-docs
build-docs: setup-dev
	mkdocs build

.PHONY: serve-docs
serve-docs: setup-dev
	mkdocs serve --dev-addr "127.0.0.1:8001"

.PHONY: build
build: setup-env clean
	python3 -m pip install --upgrade setuptools wheel
	python3 -m setup -q sdist bdist_wheel

.PHONY: install
install: build
	python3 -m pip install -q ./dist/endgame*.tar.gz
	endgame --help

.PHONY: uninstall
uninstall:
	python3 -m pip uninstall endgame -y
	python3 -m pip uninstall -r requirements.txt -y
	python3 -m pip uninstall -r requirements-dev.txt -y
	python3 -m pip freeze | xargs python3 -m pip uninstall -y

.PHONY: clean
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*.egg-link' -delete
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +

.PHONY: test
test: setup-dev
	python3 -m coverage run -m pytest -v

.PHONY: security-test
security-test: setup-dev
	bandit -r ./endgame/

.PHONY: fmt
fmt: setup-dev
	black endgame/

.PHONY: lint
lint: setup-dev
	pylint endgame/

.PHONY: publish
publish: build
	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*
	python3 -m pip install endgame

.PHONY: count-loc
count-loc:
	echo "If you don't have tokei installed, you can install it with 'brew install tokei'"
	echo "Website: https://github.com/XAMPPRocky/tokei#installation'"
	tokei ./* --exclude --exclude '**/*.html' --exclude '**/*.json'

.PHONY: terraform-demo
terraform-demo:
	cd terraform && terraform init && terraform apply --auto-approve

.PHONY: terraform-destroy
terraform-destroy:
	cd terraform && terraform destroy --auto-approve

.PHONY: integration-test
integration-test: setup-dev
	python3 -m invoke test.list-resources
	python3 -m invoke test.expose-dry-run
	python3 -m invoke test.expose
	python3 -m invoke test.expose-undo
	make terraform-destroy

