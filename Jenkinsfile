def load_conf(branch) {
    echo "Branch ${branch}"
    def config = readJSON(file: './cdk.json')

    switch(branch) {
        case 'develop':
            config["context"] = readJSON(file: './conf/dev_conf.json')
        case 'master':
            config["context"] = readJSON(file: './conf/prod_conf.json')
        default:
            config["context"] = readJSON(file: './conf/test_conf.json')
            config["context"]["PROJECT_NAME"] += '-' + env.BRANCH_NAME.split('-')[0].split('/')[1]
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
        BRANCH_ENV = "{env.BRANCH_NAME == 'develop' ? 'develop' : env.BRANCH_NAME == 'master' ? 'production' : 'none'}"
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
                sh "make init"
            }
        }
        stage('Pylint') {
            steps {
                sh "make pylint"
            }
        }
        stage('Before Deploy') {
            steps {
                sh "make beforedeploy"
            }
        }
        stage('Unit Tests') {
            steps {
                sh "make unittests"
            }
        }
        stage('Deploy') {
            when {
                expression {
                    deploy == true
                }
            }
            steps {
                sh "make deploy"
            }
        }
        stage('After Deploy') {
            when {
                expression {
                    deploy == true
                }
            }
            steps {
                sh "make afterdeploy"
            }
        }
        stage('Clear Workspace') {
            steps {
                sh "make clearworkspace"
            }
        }
    }
}
