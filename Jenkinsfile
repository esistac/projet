// Force update revision 1
pipeline {
    agent any

    environment {
        REGISTRY   = "ghcr.io"
        IMAGE_NAME = "esistac/task-manager-api"
        IMAGE_TAG  = "" 
    }

    stages {
        // Stage 1 : Récupération du code et extraction du SHA
        stage('Checkout') {
            steps {
                script {
                    IMAGE_TAG = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    echo "Démarrage du pipeline pour le commit SHA: ${IMAGE_TAG}"
                }
            }
        }

        // Stage 2 : Analyse statique de code via une image Docker Python
        stage('Lint') {
            steps {
                echo "Exécution de flake8 via un conteneur Python..."
                sh """
                    docker run --rm \
                    --volumes-from jenkins-local \
                    -w /var/jenkins_home/workspace/task-manager-pipeline \
                    python:3.11-slim sh -c '
                        pip install flake8
                        flake8 src/
                    '
                """
            }
        }

        // Stage 3 : Exécution des tests unitaires et couverture
        stage('Build & Test') {
            steps {
                echo "Exécution de pytest et génération du rapport de couverture..."
                sh """
                    docker run --rm \
                    --volumes-from jenkins-local \
                    -w /var/jenkins_home/workspace/task-manager-pipeline \
                    python:3.11-slim sh -c '
                        pip install -r requirements.txt pytest pytest-cov httpx
                        export PYTHONPATH=.
                        pytest --cov=src tests/ --cov-report=xml
                    '
                """
            }
        }

        // Stage 4 : Analyse de la qualité du code par SonarQube
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv('SonarQubeServer') {
                        sh "${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=task-manager-api \
                            -Dsonar.sources=src/ \
                            -Dsonar.tests=tests/ \
                            -Dsonar.python.coverage.reportPaths=coverage.xml"
                    }
                }
            }
        }

        // Stage 5 : Blocage si la barrière de qualité échoue
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // Stage 6 : Analyse de vulnérabilités sur l'image Docker locale
        stage('Security Scan') {
            steps {
                echo "Construction de l'image pour scan..."
                sh "docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
                echo "Exécution du scan de sécurité avec Trivy via Docker..."
                sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity CRITICAL ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        // Stage 7 : Publication de l'image (uniquement sur la branche main)
        stage('Push Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    try {
                        withCredentials([usernamePassword(credentialsId: 'github-ghcr-creds', usernameVariable: 'GH_USER', passwordVariable: 'GH_TOKEN')]) {
                            sh "echo ${GH_TOKEN} | docker login ${REGISTRY} -u ${GH_USER} --password-stdin"
                            sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                            sh "docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest"
                            sh "docker push ${REGISTRY}/${IMAGE_NAME}:latest"
                        }
                    } catch (Exception e) {
                        echo "⚠️ Échec du push : Assurez-vous d'avoir configuré le credential 'github-ghcr-creds' dans Jenkins."
                    }
                }
            }
        }

        // Stage 8 : Déploiement de l'Infrastructure via Terraform
        stage('IaC Apply') {
            steps {
                echo "Initialisation et application Terraform via Docker..."
                sh """
                    docker run --rm \
                    --volumes-from jenkins-local \
                    -w /var/jenkins_home/workspace/task-manager-pipeline/infra \
                    hashicorp/terraform:1.7.0 init
                    
                    docker run --rm \
                    --volumes-from jenkins-local \
                    -w /var/jenkins_home/workspace/task-manager-pipeline/infra \
                    hashicorp/terraform:1.7.0 apply -var="image_tag=${IMAGE_TAG}" -auto-approve
                """
            }
        }
    }

    post {
        always {
            echo "Nettoyage de l'espace de travail..."
            cleanWs()
        }
        success {
            echo "Pipeline exécuté avec succès ! 🎉"
        }
        failure {
            echo "Le pipeline a échoué. ❌"
        }
    }
}