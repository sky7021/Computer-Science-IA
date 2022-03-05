from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from main import db
from main.auth import bp
from main.auth.forms import LoginForm, CreateForm, DeleteForm
from main.models import Admin

@bp.route('/login', methods=['GET', 'POST'])
def login():

    #logged in user tries to access login page
    if current_user.is_authenticated:
        return redirect(url_for('auth.homepage'))

    form = LoginForm()
    if form.validate_on_submit():
        #check for username in Profiles database
        admin = Admin.query.filter_by(username=form.username.data).first()

        #if found, check that password matches for password of username
        if admin == None or not admin.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(admin)
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            return redirect(url_for('auth.homepage'))
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign in', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.homepage'))
    
    form = CreateForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        admin = Admin(username=username)
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        flash('Account created')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Create admin', form=form)

@bp.route('/')
@bp.route('/homepage/')
@login_required
def homepage():
    #TODO: bring up all the fumos that the Profile owns
    return render_template('auth/homepage.html')
    
#modify delete account to delete user profiles
@bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(current_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    
    return render_template('auth/delete_account.html', title='Account Deleteion', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.homepage'))