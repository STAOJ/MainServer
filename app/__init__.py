from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

import rq
from redis import Redis
from config import Config

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_ckeditor import CKEditor, CKEditorField


app = Flask(__name__)
app.config.from_object(Config)

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Redis setup
app.redis = Redis.from_url(app.config["REDIS_URL"])
app.task_queue = rq.Queue("evaluation-tasks", connection=app.redis)

# Flask Login setup
login = LoginManager(app)
login.login_view = "login"

from app.models import User, Problem, Contest, Registration, Submission, Announcement, SampleCase

# Flask Admin setup
ckeditor = CKEditor(app)
admin = Admin(app, template_mode='bootstrap3')

# BetterView allows us to use a more advanced text editor
class BetterView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated # and current_user.is_admin

    form_overrides = dict(body=CKEditorField)
    create_template = 'edit.html'
    edit_template = 'edit.html'

# Setting up the administrators page
admin.add_view(BetterView(Announcement, db.session))
admin.add_view(BetterView(User, db.session))
admin.add_view(BetterView(Problem, db.session))
admin.add_view(BetterView(Contest, db.session))
admin.add_view(BetterView(Registration, db.session))
admin.add_view(BetterView(Submission, db.session))
admin.add_view(BetterView(SampleCase, db.session))

from app import routes, models
