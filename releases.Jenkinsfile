pipeline {
    agent any

    parameters { string(name: 'POLYBOT_PROD_IMG_URL', defaultValue: '', description: '') }

    stages{
        stage('Update YAML') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github2', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    sh '''
                    git checkout releases
                    git merge origin/main

                    sed -i 's/image: .*/image: $POLYBOT_PROD_IMG_URL/g' k8s/polybot/polybot_deployment.yaml

                    git add k8s/polybot/polybot_deployment.yaml
                    git -c user.name='jihadarfat' -c user.email=arfatjoj@gmail.com commit -m "POLYBOT_PROD_IMG_URL"
                    git push https://JihadArfat:$PASSWORD@github.com/JihadArfat/k8s_project.git releases
                    '''
                }
            }
        }
    }
}