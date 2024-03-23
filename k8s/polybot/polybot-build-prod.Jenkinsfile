pipeline {
    agent any

    environment {
        ECR_URL = "352708296901.dkr.ecr.us-west-1.amazonaws.com"
    }

    stages{
        stage('Build') {
            steps {
                sh '''
                cd k8s/polybot
                aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin 352708296901.dkr.ecr.us-west-1.amazonaws.com
                docker build -t $ECR_URL/jihadpolybot:0.0.$BUILD_NUMBER .
                docker push $ECR_URL/jihadpolybot:0.0.$BUILD_NUMBER
                '''
            }
        }
    }
}