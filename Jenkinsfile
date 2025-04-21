pipeline {
    agent any

    environment {
        IMAGE_NAME = 'coffee-flask-app'
        CONTAINER_NAME = 'coffee-prod-5001'
        HOST_PORT = '5001'
        CONTAINER_PORT = '5000'
    }

    stages {
        stage('Clone Repo') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t $IMAGE_NAME ."
                }
            }
        }

        stage('Stop & Remove Old Container') {
            steps {
                script {
                    sh "docker stop $CONTAINER_NAME || true"
                    sh "docker rm $CONTAINER_NAME || true"
                }
            }
        }

        stage('Run Container on Port 5001') {
            steps {
                script {
                    sh """
                        docker run -d \
                        --name $CONTAINER_NAME \
                        -p $HOST_PORT:$CONTAINER_PORT \
                        $IMAGE_NAME
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed.'
        }
    }
}
