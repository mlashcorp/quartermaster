from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView
from flask_mongoengine import MongoEngine
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CsrfProtect

#import os
#basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = MongoEngine(app)
udb = SQLAlchemy(app)

admin = Admin(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

csrf = CsrfProtect(app)

from tracker import models, views

admin.add_view(ModelView(models.SoftwareRequirement))
admin.add_view(ModelView(models.Issue))
admin.add_view(ModelView(models.Test))

admin.add_view(ModelView(models.IssueType))
admin.add_view(ModelView(models.IssueStatus))
admin.add_view(ModelView(models.TestType))
admin.add_view(ModelView(models.TestStatus))

admin.add_view(ModelView(models.SoftwarePackage))
admin.add_view(ModelView(models.SoftwareComponent))

admin.add_view(ModelView(models.DeviceVersion))

admin.add_view(ModelView(models.Release))
admin.add_view(ModelView(models.ReleaseStatus))
admin.add_view(ModelView(models.SoftwareBundle))

import jobs

