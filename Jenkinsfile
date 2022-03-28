def load_conf(branch) {
    def config = readJSON(file: './cdk.json')
    echo branch
    echo readFile('./cdk.json')
    echo ("Branch ${branch}")
    switch(branch) {
        case branch = 'develop':
            config["context"] = reasJSON(file: './conf/dev_conf.json')
            break
        case branch = 'master':
            config["context"] = reasJSON(file: './conf/prod_conf.json')
            break
        default:
            config["context"] = reasJSON(file: './conf/test_conf.json')
            config["context"]["SUFFIX"] += '-' + env.BRANCH_NAME.split('-')[0].split('/')[1]
            break
    }

    env.SUFFIX = config["context"]["SUFFIX"]
    env.AWS_REGION = config["context"]["AWS_REGION"]

    writeJSON file: './cdk.json', json:config, pretty: 4
    echo (readFile('./cdk.json'))
}


pipeline {
    agent any

    environment {
        HOME = "${env.WORKSPACE}"
        BRANCH_ENV = "{env.BRANCH_NAME == 'develop' ? 'develop' : env.BRANCH_NAME == 'master' ? 'production' : 'none'}"

    }

    stages {
        stage('SCM') {
            steps {
                checkout scm
            }
        }
        stage('Check Deploy') {
            steps {
                script {
                    deploy = true
                    git_commit_message = sh(returnStdout: true, script: 'git show -s --format=%B -1').trim()

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
