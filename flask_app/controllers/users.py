from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User
from flask_app.models.band import Band
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def log_and_reg():
    return render_template("log_and_reg.html")

@app.route('/login', methods=['POST'])
def login():
    if not User.validate_login(request.form):
        return redirect('/')
    user = User.get_user_by_email(request.form)
    if user:
        if not bcrypt.check_password_hash(user.password, request.form['password']):
            flash('Email/password combination is incorrect')
            return redirect('/')

        session['user_id'] = user.id
        flash('Login was succesful')
        return redirect('/dashboard')

    flash('Email is not tied to an account')
    return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    if not User.validate_register(request.form):
        return redirect('/')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)
    register_data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': pw_hash
    }

    user_id = User.register_user(register_data)
    session['user_id'] = user_id
    flash('Registration was successful')
    return redirect('/dashboard')

@app.route('/bands/<int:id>/mybands')
def show_band(id):
    band_data = {
        'id': id
    }
    user_data = {
        'id': session['user_id']
    }
    return render_template("show_band.html", user=User.get(band_data), member = User.get_user_with_bands(user_data))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')