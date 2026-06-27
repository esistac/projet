pipeline {
    agent any

    environment {
        // Variables globales pour le pipeline
        REGISTRY          = "ghcr.io"
        IMAGE_NAME        = "esistac/task-manager-api"
        SCANNER_HOME      = tool 'SonarQubeScanner' // Nom du scanner configuré dans Jenkins
        IMAGE_TAG         = "" // Sera défini dynamiquement par le SHA du commit
    }

    stages {
        // Stage 1 : Récupération du code et extraction du SHA
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    // Récupération des 7 premiers caractères du SHA du commit Git
                    IMAGE_TAG = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    echo "Démarrage du pipeline pour le commit SHA: ${IMAGE_TAG}"
                }
            }
        }

        // Stage 2 : Analyse statique de code (Linting Python)
        stage('Lint') {
            steps {
                echo "Exécution de flake8..."
                // Utilise le conteneur ou l'environnement local pour linter
                sh "pip install flake8 && flake8 src/"
            }
        }

        // Stage 3 : Exécution des tests unitaires et couverture
        stage('Build & Test') {
            steps {
                echo "Exécution de pytest avec couverture de code..."
                sh "pip install -r requirements.txt pytest pytest-cov httpx"
                sh "pytest --cov=src tests/ --cov-report=xml"
            }
        }

        // Stage 4 : Analyse de la qualité du code par SonarQube
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQubeServer') { // Nom de ton serveur Sonar dans Jenkins
                    sh "${SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=task-manager-api \
                        -Dsonar.sources=src/ \
                        -Dsonar.tests=tests/ \
                        -Dsonar.python.coverage.reportPaths=coverage.xml"
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
                echo "Construction temporaire de l'image pour scan..."
                sh "docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
                echo "Exécution du scan de sécurité avec Trivy..."
                // Scan de l'image en bloquant uniquement si des vulnérabilités CRITICAL sont trouvées
                sh "trivy image --severity CRITICAL --exit-code 1 ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        // Stage 7 : Publication de l'image (uniquement sur la branche main)
        stage('Push Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "Connexion au registre GHCR et push de l'image..."
                    withCredentials([usernamePassword(credentialsId: 'github-ghcr-creds', usernameVariable: 'GH_USER', passwordVariable: 'GH_TOKEN')]) {
                        sh "echo ${GH_TOKEN} | docker login ${REGISTRY} -u ${GH_USER} --password-stdin"
                        sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                        // Ajout du tag latest pour le suivi standard
                        sh "docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest"
                        sh "docker push ${REGISTRY}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        // Stage 8 : Déploiement de l'Infrastructure via Terraform
        stage('IaC Apply') {
            steps {
                dir('infra') {
                    echo "Initialisation et application Terraform..."
                    sh "terraform init"
                    // On injecte dynamiquement le tag d'image récupéré au Stage 1
                    sh "terraform apply -var='image_tag=${IMAGE_TAG}' -auto-approve"
                }
            }
        }

        // Stage 9 : Validation finale du bon fonctionnement de l'infrastructure
        stage('Smoke Test') {
            steps {
                echo "Attente du démarrage du conteneur..."
                sleep time: 5, unit: 'SECONDS'
                echo "Exécution du Smoke Test sur l'endpoint /health..."
                // Appel curl sur l'infra déployée en Staging (port 8000)
                sh "curl -f http://localhost:8000/health"
            }
        }
    }

    post {
        always {
            echo "Nettoyage de l'espace de travail..."
            cleanWs()
        }
        success {
            echo "Pipeline exécuté avec succès ! 🎉 Le Task Manager est déployé en staging."
        }
        failure {
            echo "Le pipeline a échoué. Vérifiez les logs des étapes ci-dessus. ❌"
        }
    }
}
# Mise a jour du pipeline