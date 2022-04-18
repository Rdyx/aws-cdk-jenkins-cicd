def load_conf(branch) {
    echo "Branch ${branch}."
    def config = readJSON(file: './cdk.json')

    switch(branch) {
        case 'develop':
            config["context"] = readJSON(file: './conf/dev_conf.json')
        case 'master':
            config["context"] = readJSON(file: './conf/prod_conf.json')
        default:
            config["context"] = readJSON(file: './conf/test_conf.json')
            config["context"]["STAGE"] += '-' + env.BRANCH_NAME.split('-')[0].split('/')[1]
    }

    env.PROJECT_NAME = config["context"]["PROJECT_NAME"]
    env.AWS_DEFAULT_REGION = config["context"]["AWS_DEFAULT_REGION"]

    writeJSON file:'./cdk.json', json:config, pretty: 2
    echo readFile('./cdk.json')
}


pipeline {
    agent any

    tools {nodejs "nodejs"}

    environment {
        BRANCH_ENV = "${env.BRANCH_NAME == 'develop' ? 'develop' : env.BRANCH_NAME == 'master' ? 'production' : 'none'}"
    }

    stages {
        stage('Check Deploy') {
            steps {
                script {
                    deploy = true
                    git_commit_message = sh(returnStdout: true, script: 'git show -s --format=%B -1').trim()
                    echo ("Commit: ${git_commit_message}")

                    if (git_commit_message.endsWith("NODEPLOY") && BRANCH_ENV == 'none') {
                        echo "This build will not be deployed."
                        deploy = false
                    }
                }
            }
        }
        stage('Load Conf') {
            steps {
                load_conf(env.BRANCH_NAME)
            }
        }
        stage('Init') {
            steps {
                sh "pip3 install --upgrade awscli --user"
                sh "pip3 install -r requirements.txt --user"
            }
        }
        stage('Pylint') {
            steps {
                sh "python3 -m pylint -rn \
                        --rcfile=utils_files/.pylintrc \
                        --fail-under=5.50 \
                        --msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}' \
                        --ignore-paths=back/lambdas_layers \
                        ./back/* \
                        ./back/lambdas/* \
                        ./front/*"
            }
        }
        stage('Unit Tests') {
            steps {
                sh "python3 -m tox"
            }
        }
        stage('Before Deploy') {
            when {
                expression {
                    deploy == true
                }
            }
            steps {
                sh "python3 utils_files/before_deploy/before_deploy.py"
            }
        }
        stage('Build Lambdas Layers') {
            when {
                expression {
                    deploy == true
                }
            }
            steps {
                sh "python3 utils_files/build_layers/build_lambdas_layers.py --path back/lambdas_layers"
            }
        }
        stage('Deploy') {
            when {
                expression {
                    deploy == true
                }
            }
            steps {
                sh "cdk synth"
                sh "cdk bootstrap"
                sh "cdk deploy --all --require-approval=never --outputs-file deploy-output.json"
            }
        }
        stage('After Deploy') {
            when {
                expression {
                    deploy == true
                }
            }
            steps {
                sh "python3 utils_files/after_deploy/after_deploy.py"
            }
        }
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
    }
}
