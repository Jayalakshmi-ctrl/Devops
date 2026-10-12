pipeline {
    agent any

    environment {
        IMAGE_NAME = 'gym-app-v1'
        IMAGE_TAG  = 'latest'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo 'Pulling code from GitHub Repository...'
                checkout scm
            }
        }

        stage('Docker Image Assembly') {
            steps {
                echo 'Assembling the production Docker container...'
                // This builds the environment container completely, automatically baking your dependencies inside
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Execute Unit Tests') {
            steps {
                echo 'Running automated Pytest Validation Suite inside the container container...'
                // This runs the test runner inside the isolated container where python is guaranteed to exist
                sh "docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest --verbose"
            }
        }
    }

    post {
        success {
            echo "CI Workflow Completed Successfully. Quality Gate Passed!"
        }
        failure {
            echo "Pipeline Deployment Fault Detected. Checking logs..."
        }
    }
}
