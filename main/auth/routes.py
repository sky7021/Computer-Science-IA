from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from main import db
from main.auth import bp
from main.auth.forms import LoginForm, CreateForm, DeleteForm
from main.models import Admin, Profile, Order

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

        #logs user in (built in function)
        login_user(admin)
        #requested page prior to login
        next_page = request.args.get('next')
        
        #page must be on the same site 
        if not next_page or url_parse(next_page).netloc != '':
            return redirect(url_for('auth.homepage'))
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign in', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    #current admins cannot create accounts
    if current_user.is_authenticated:
        return redirect(url_for('auth.homepage'))
    
    form = CreateForm()

    if form.validate_on_submit():
        #gets info from form
        username = form.username.data
        password = form.password.data

        #creates new Admin object
        admin = Admin(username=username)
        admin.set_password(password)

        #adds it to database
        db.session.add(admin)
        db.session.commit()

        flash('Account created')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Create admin', form=form)

@bp.route('/')
@bp.route('/homepage/')
@login_required
def homepage():
    #int page var from URL, default 1
    page = request.args.get('page', 1, type=int)

    #paginates all Profile entries, renders int amount in PROFILES_PER_PAGE for the current page, page. 
    #False returns empty list instead of crashing
    profiles = Profile.query.paginate(
        page, current_app.config['PROFILES_PER_PAGE'], False
    )

    #same as above but for orders
    orders = Order.query.paginate(
        page, current_app.config['ORDERS_PER_PAGE'], False
    )

    #length of list of items currently shown on page
    l_profiles = len(profiles.items)
    l_orders = len(orders.items)
    
    #table with most entries is used for rendering the table
    if l_profiles < l_orders:
        longest = l_orders
    else:
        longest = l_profiles

    #table with subsequent pages is used for pagination to cover all pages
    if profiles.has_next:
        pagination = profiles
    else:
        pagination = orders

    #passes variables to be rendered in template
    return render_template('auth/homepage.html', profiles = profiles.items, orders = orders.items, longest = longest, pagination = pagination,
    l_profiles = l_profiles, l_orders = l_orders, round = round
    )
    
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