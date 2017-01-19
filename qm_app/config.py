from tracker import app
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

app.config['MONGODB_SETTINGS'] = {
    'db': 'tracker',
    'host': 'localhost',
    'port': 27017
}

GOOGLE_LOGIN_CLIENT_ID = "527669077845-7mu8jjidbaoh3rengr7mab386p3i4a61.apps.googleusercontent.com"
GOOGLE_LOGIN_CLIENT_SECRET = "-I3szYev66fL82DiQhglMNsp"

OAUTH_CREDENTIALS={
        'google': {
            'id': GOOGLE_LOGIN_CLIENT_ID,
            'secret': GOOGLE_LOGIN_CLIENT_SECRET
        }
}

CSRF_ENABLED = True
SECRET_KEY = 'biosurfit'
