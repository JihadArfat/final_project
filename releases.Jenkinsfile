pipeline {
    agent any

    parameters { string(name: 'POLYBOT_PROD_IMG_URL', defaultValue: '', description: '') }

    stages{
        stage('Update YAML') {
            steps {
                sh '''
                sed -i 's/image: .*/image: $POLYBOT_PROD_IMG_URL/g' k8s/polybot/polybot_deployment.yaml

                cat k8s/polybot/polybot_deployment.yaml
                git checkout releases
                git merge main
                git add k8s/polybot/polybot_deployment.yaml
                git commit -m "POLYBOT_PROD_IMG_URL"
                git push origin releases
                '''
            }
        }
    }
}