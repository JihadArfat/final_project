pipeline {
    agent any

    parameters {
        string(name: 'IMG_URL', defaultValue: '', description: '')
    }

    stages {
        stage('Update YAML') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github2', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    script {
                        def yamlFile

                        if (IMG_URL.contains("polybot")) {
                            yamlFile = "k8s/polybot/polybot_deployment.yaml"
                        } else if (IMG_URL.contains("yolo5")) {
                            yamlFile = "k8s/yolo5/yolo5_deployment.yaml"
                        } else {
                            error('Invalid IMG_URL')
                        }

                        sh '''
                        printenv

                        git checkout releases
                        git merge origin/main
                        echo "yamlFile: ${yamlFile}"
                        ls -l k8s/polybot/
                        ls -l k8s/yolo5/
                        pwd
                        sed -i "s|image: .*|image: ${IMG_URL}|g" "${yamlFile}"
                        git add "${yamlFile}"
                        git -c user.name='jihadarfat' -c user.email=arfatjoj@gmail.com commit -m "$IMG_URL"
                        git push https://JihadArfat:${PASSWORD}@github.com/JihadArfat/k8s_project.git releases
                        '''
                    }
                }
            }
        }
    }
}
