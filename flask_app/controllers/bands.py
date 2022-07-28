import re
from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User
from flask_app.models.band import Band
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route("/dashboard")
def user_dashboard():
    if 'user_id' not in session:
        return redirect('/')
    user_data = {
        'id': session['user_id']
    }
    user = User.get_user_with_bands(user_data)
    bands = Band.get_all()
    return render_template('dashboard.html', user=user, bands=bands)

@app.route('/bands/sighting')
def new_band_form():
    if 'user_id' not in session:
        return redirect('/dashboard')
    user_data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(user_data)
    return render_template('create_band.html', user=user)

@app.route('/bands/create', methods=['POST'])
def create_band():
    if not Band.validate_create(request.form):
        return redirect('/bands/sighting')
    Band.create(request.form)
    return redirect('/dashboard')

@app.route('/bands/<int:id>/edit')
def show_edit_form(id):
    user_data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(user_data)
    band_data = {
        'id': id
    }
    band = Band.get_one(band_data)
    return render_template('edit_band.html', user=user, band=band)

@app.route('/bands/<int:id>/update', methods=['POST'])
def update_band(id):
    if not Band.validate_update(request.form):
        return redirect(f'/bands/{id}/edit')
    Band.update(request.form)
    return redirect('/dashboard')

@app.route('/bands/<int:id>/delete')
def delete(id):
    band_data = {
        'id': id
    }
    Band.delete(band_data)
    return redirect("/dashboard")

@app.route('/bands/<int:id>/join')
def join(id):
    band_data = {
        'id': id,
        'user_id': session['user_id']
    }
    Band.join(band_data)
    return redirect('/dashboard')

@app.route('/bands/<int:id>/quit')
def quit(id):
    band_data = {
        'id': id,
        'user_id': session['user_id']
    }
    Band.quit(band_data)
    return redirect('/dashboard')