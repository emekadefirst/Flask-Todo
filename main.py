from model import db, app, Todo, User
from flask import render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, login_manager, LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from dotenv import load_dotenv

load_dotenv()


key = os.environ.get('app_key')
app.secret_key = key

login_manager = LoginManager()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

login_manager.init_app(app)

@app.route("/home", methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        note = request.form['data']
        date = request.form['date']
        todo = Todo(data=note, date=date, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('create'))
    
    todos = current_user.todo
    return render_template('index.html', user=current_user, todos=todos)



@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    todo = Todo.query.get_or_404(id)
    if todo and todo.user_id == current_user.id:
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for("create"))
    return render_template('index.html', user=current_user)

@app.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update(id):
    todo = Todo.query.get_or_404(id)
    if todo and todo.user_id == current_user.id:
        if request.method == "POST":
            todo.data = request.form['data']
            todo.date = request.form['date']
            db.session.commit()
            return redirect(url_for("create"))
    return render_template('update.html', user=current_user, todo=todo)



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('create'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        if password1 == password2:
            user = User(email=email, username=username, password=generate_password_hash(password1))
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            return redirect('home')
    return render_template('sign-up.html')


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('login'))  # Redirect to the login endpoint


admin = Admin(app, name='', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Todo, db.session))

if __name__ == "__main__":
    app.run(debug=True)



