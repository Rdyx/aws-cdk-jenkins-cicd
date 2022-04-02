SHELL = /bin/sh

init:
	pip3 install --upgrade awscli --user
	pip3 install -r requirements.txt --user

pylint:
	python3 -m pylint -rn \
		--rcfile=utils_files/.pylintrc \
		--fail-under=5.50 \
		--msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}' \
		./back \
		./back/lambdas \
		./front

beforedeploy:
	python3 utils_files/before_deploy/before_deploy.py

unittests:
	python3 -m tox

buildlayers:
	python3 utils_files/build_layers/build_lambdas_layers.py --path back/lambdas_layers

deploy:
	cdk synth
	cdk bootstrap
	cdk deploy --all --require-approval=never --outputs-file deploy-output.json

afterdeploy:
	python3 utils_files/after_deploy/after_deploy.py
