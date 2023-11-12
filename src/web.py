import flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = flask.Flask(__name__)

db_uri = os.environ.get("DB_URI")
if not db_uri:
    raise ValueError("dburi env not set")

app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True

db = SQLAlchemy(app)
admin = Admin(app)


class Hub(db.Model):
    __tablename__ = "hubs"
    id = db.Column(db.Integer, primary_key=True)
    hub_url = db.Column(db.Text)


class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    article_url = db.Column(db.Text, unique=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    author_url = db.Column(db.Text)
    author_username = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    hub = db.Column(db.Text)


class ArticleView(ModelView):
    can_create = False
    can_edit = False
    column_exclude_list = [
        "body",
    ]
    column_searchable_list = ["title", "author_username", "hub"]


admin.add_view(ModelView(Hub, db.session))
admin.add_view(ArticleView(Article, db.session))

with app.app_context():
    db.create_all()

app.run(host="0.0.0.0")
