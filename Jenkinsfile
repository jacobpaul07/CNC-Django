pipeline{

	agent any

	environment {
		DOCKERHUB_CREDENTIALS=credentials('docker_hub_siqsessedge_with_token')
	}

	stages {

		stage('Build') {

			steps {
				sh 'docker build -t siqsessedge/cnc-api:CNC-v9.0 . --no-cache'
			}
		}

		stage('Login') {

			steps {
				sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
			}
		}

		stage('Push') {

			steps {
				sh 'docker push siqsessedge/cnc-api:CNC-v9.0'
			}
		}
	}

	post {
		always {
			sh 'docker logout'
		}
	}

}