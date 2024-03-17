from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yuvalco1'
login_manager = LoginManager()
login_manager.init_app(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False



with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/')
def home():
    return render_template("index.html",logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        print(name)
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user:
            flash("Email already exists, please Login")
            return redirect(url_for('login'))
        else:
            to_add_user = User(name=request.form.get('name'), email=request.form.get('email'),
                               password=generate_password_hash(request.form['password'], method="pbkdf2", salt_length=8))
            db.session.add(to_add_user)
            db.session.commit()
            print(to_add_user.id)
            login_user(to_add_user, remember=True)
            flash("User created successfully")
            return redirect(url_for('secrets', name=name))
    return render_template("register.html",logged_in=current_user.is_authenticated)


@app.route('/login',methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password_entered = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password_entered):
            print("Login Successful")
            flash("Logged in successfully")
            print(user.password)
            print(generate_password_hash(password_entered, method="pbkdf2", salt_length=8))
            print(check_password_hash(user.password, password_entered))
            print(user)
            login_user(user, remember=True)
            return redirect(url_for('secrets', name=user.name))
        else:
            flash("Login unsuccessful. Please check username and password")
            return redirect(url_for('login'))

    return render_template("login.html",logged_in=current_user.is_authenticated)


@app.route('/secrets/<name>')
@login_required
def secrets(name):
    print(name)
    return render_template("secrets.html", name=name,logged_in=True, cheet_sheet_file_path="static/files/cheat_sheet.pdf")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/download')
@login_required
def download():
    return send_from_directory('static', path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
