pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        GEMINI_API_KEY = credentials('AIzaSyALUVHO6Cww7e8TmrS9elxx6UWGBDmFpAk')
        SECRET_KEY = credentials('SECRET_KEY_ID')
        DATABASE_URL = credentials('DATABASE_URL_ID')
    }

    stages {

        stage('Checkout') {
            steps {
                git url: 'https://github.com/haichteque/student-management-using-django.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                // Create virtual environment and install dependencies
                sh 'python3 -m venv $VENV_DIR'
                sh 'source $VENV_DIR/bin/activate && pip install --upgrade pip'
                sh 'source $VENV_DIR/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Server') {
            steps {
                // Start Django development server in the background
                sh '''
                source $VENV_DIR/bin/activate
                nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
                sleep 5
                '''
            }
        }

        stage('Check Server Running') {
            steps {
                // Simple check if server is listening on port 8000
                sh '''
                if nc -zv localhost 8000; then
                    echo "Server is running"
                else
                    echo "Server failed to start"
                    exit 1
                fi
                '''
            }
        }

        stage('Run Tests & Generate Reports') {
            steps {
                // Run the tester_and_reporter.py script
                sh 'source $VENV_DIR/bin/activate && python tester_and_reporter.py'
            }
        }
    }

    post {
        success {
          echo "Build Passed."
        }
        failure {
          echo "Build Failed"
        }
        cleanup {
            // Kill Django server after build
            sh 'pkill -f "manage.py runserver" || true'
        }
    }
}
