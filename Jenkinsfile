pipeline {
    agent any

    environment {
        IMAGE_NAME = 'coffee-flask-app'      // Set your image name
        CONTAINER_NAME = 'coffee-prod-5001'  // Set your container name
        HOST_PORT = '5018'                   // Host port
        CONTAINER_PORT = '5000'              // Container port (Flask runs on port 5000)
    }

    stages {
        stage('Clone Repo') {
            steps {
                echo 'Cloning repository...'
                // Jenkins will clone the repo automatically if using pipeline from SCM
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

        stage('Run Container on Port 5018') {
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
