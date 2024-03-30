pipeline {
    agent any

    parameters {
        string(name: 'IMG_URL', defaultValue: '', description: '')
    }

    stages {
        stage('Update YAML') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github2', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        sh '''
                        printenv

                        if [[ $IMG_URL == *"polybot"* ]]; then
                            yamlFile="k8s/polybot/polybot_deployment.yaml"
                        elif [[ $IMG_URL == *"yolo5"* ]]; then
                            yamlFile="k8s/yolo5/yolo5_deployment.yaml"
                        else
                            exit 7
                        fi

                        # Checkout releases and merge with main, handling conflicts
                        git checkout releases
                        if git merge origin/main; then
                            # No conflicts, update the YAML file and push changes
                            sed -i "s|image: .*|image: ${IMG_URL}|g" "${yamlFile}"
                            git add "${yamlFile}"
                            git -c user.name='jihadarfat' -c user.email=arfatjoj@gmail.com commit -m "$IMG_URL"
                            git push https://JihadArfat:${PASSWORD}@github.com/JihadArfat/final_project.git releases

                            # Switch back to main and push the rebased changes
                            git checkout main
                            git pull origin releases --rebase
                            git push https://JihadArfat:${PASSWORD}@github.com/JihadArfat/final_project.git main
                        else
                            # Handle merge conflict by aborting the merge
                            git merge --abort
                            echo "Merge conflict detected. Aborting merge."
                            exit 1
                        fi
                        '''
                }
            }
        }
    }
}