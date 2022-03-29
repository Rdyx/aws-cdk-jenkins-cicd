SHELL = /bin/sh

init:
	pip3 install --upgrade awscli --user
	pip3 install -r requirements.txt --user

pylint:
	python3 -m pylint -rn \
		--rcfile=utils_files/.pylintrc \
		--fail-under=9.50 \
		--msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}' \
		./back \
		./back/lambdas \
		./front

beforedeploy:
	python3 utils_files/before_deploy/build_lambdas_layers.py --path back/lambdas_layers

unittests:
	python3 -m tox

deploy:
	cdk synth
	cdk bootstrap
	cdk deploy --all --require-approval=never --outputs-file deploy-output.json

afterdeploy:
	python3 utils_files/after_deploy/after_deploy.py

clearworkspace:
	python3 utils_files/clearworkspace/clear_workspace.py