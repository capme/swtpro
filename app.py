#!/usr/bin/env python3

from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from dotenv import load_dotenv
import os


DEVELOPMENT_ENV = True

load_dotenv() 

app = Flask(__name__)

# ENV CREDS
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")

# flask app config
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://{}:{}@database:3306/{}".format(MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = os.path.join('static', UPLOAD_FOLDER)
Session(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# DB Models
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True, index=True)
    password = db.Column(db.String(255)) #sha256

class ImageUpload(db.Model):
    __tablename__ = 'image_upload'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    path_image = db.Column(db.String(100))


# validate field usernamw
def validate_username(param):
    whitelist = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0','.', '_']

    if set(param) <= set(whitelist):
        return True
    return False

# validate field password
def validate_password(param):
    whitelist = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0','.','!', '_']

    if set(param) <= set(whitelist):
        return True
    return False


# Route URLs
@app.route("/")
def index():
    if not session.get("name") and not session.get("id"):
        return redirect("/login")

    return redirect("/home")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        # sanitize username field input
        if not validate_username(username):
            app_data = {
                "app_message": "Please use combination of alphanumeric and dot (.) for field username.",
            }
            return render_template("register.html", app_data=app_data)

        # sanitize password field input
        if not validate_password(password):
            app_data = {
                "app_message": "Please use combination of alphanumeric, dot (.), '!', '_' for field password.",
            }
            return render_template("register.html", app_data=app_data)

        if username and password and confirm_password:
            if password == confirm_password:
                hashed_password = generate_password_hash(
                    password, "pbkdf2:sha256")
                try:
                    new_user = Users(
                        username=username,
                        password=hashed_password,
                    )

                    db.session.add(new_user)
                    db.session.commit()
                except exc.IntegrityError:
                    app_data = {
                        "app_message": "Username already exist!",
                    }

                app_data = {
                    "app_message": "User created!",
                }
            else:
                app_data = {
                    "app_message": "Confirmation password not equal!",
                }
        else:
            app_data = {
                "app_message": "Please fill the field data!",
            }
    else:
        app_data = {
            "app_message": "",
        }

    return render_template("register.html", app_data=app_data)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # sanitize username field input
        if not validate_username(username):
            app_data = {
                "app_message": "Please use valid username.",
            }
            return render_template("login.html", app_data=app_data)

        # sanitize password field input
        if not validate_password(password):
            app_data = {
                "app_message": "Please use valid password.",
            }
            return render_template("login.html", app_data=app_data)


        user = Users.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                session["name"] = username
                session["id"] = user.id
                return redirect("/home")
            else:
                app_data = {
                    "app_message": "Incorrect password!",
                }
                return render_template("login.html", app_data=app_data)
        else:
            app_data = {
                "app_message": "Username not found!",
            }
            return render_template("login.html", app_data=app_data)
    else:
        app_data = {
            "app_message": "",
        }
        return render_template("login.html", app_data=app_data)


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if not session.get("name") and not session.get("id"):
        return redirect("/login")

    if request.method == 'POST':
        f = request.files['file']

        if not f:
            app_data = {
                "app_message": "Please select image to be uploaded!",
            }
            return render_template("upload.html", app_data=app_data)

        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
        image_upload = ImageUpload(
            id_user=session["id"],
            path_image=full_filename,
        )

        db.session.add(image_upload)
        db.session.commit()

        f.save(os.path.join(app.config["UPLOAD_FOLDER"], f.filename))
        
        app_data = {
            "app_message": "Success upload file {}".format(f.filename),
        }
        return render_template("upload.html", app_data=app_data)
    else:
        app_data = {
            "app_message": "",
        }
        return render_template("upload.html", app_data=app_data)


@app.route('/delete/<id_record_file>')
def delete_file(id_record_file):
    if not session.get("name") and not session.get("id"):
        return redirect("/login")

    # removing the file
    img = ImageUpload.query.filter_by(id=id_record_file).first()
    os.remove(img.path_image)

    # delete the db record
    ImageUpload.query.filter_by(id=id_record_file).delete()
    db.session.commit()

    return redirect("/home")


@app.route("/logout")
def logout():
    session["name"] = None
    session["id"] = None
    return redirect("/")


@app.route("/home")
def home():
    if not session.get("name") and not session.get("id"):
        return redirect("/login")

    app_data = {
        "app_message": "",
    }

    # getting list images for certain user
    list_images = ImageUpload.query.filter_by(id_user=session.get("id")).all()
    app_data["images"] = list_images

    return render_template("home.html", app_data=app_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=DEVELOPMENT_ENV)
