from main import app, db
from flask import render_template, redirect, url_for, request, flash, request
from main.forms import DeleteOrderForm, EditOrderForm, OrderProfileForm, LoginForm, CreateForm, DeleteForm, MakeOrderForm, SearchOrderForm, SearchProfileForm
from flask_login import logout_user, current_user, login_user, login_required
from main.models import Admin, Profile, Order
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/homepage/')
@login_required
def homepage():
    #TODO: bring up all the fumos that the Profile owns

    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    #logged in user tries to access login page
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = LoginForm()
    if form.validate_on_submit():
        #check for username in Profiles database
        admin = Admin.query.filter_by(username=form.username.data).first()

        #if found, check that password matches for password of username
        if admin == None or not admin.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(admin)
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            return redirect(url_for('homepage'))
        return redirect(next_page)

    return render_template('login.html', title='Sign in', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    
    form = CreateForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        admin = Admin(username=username)
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        flash('Account created')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Create profile', form=form)

#modify delete account to delete user profiles
@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(current_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('delete_account.html', title='Account Deleteion', form=form)

@app.route('/deleteorder/<name>', methods=['GET', 'POST'])
@login_required
def deleteorder(name):
    form = DeleteOrderForm()

    if form.validate_on_submit():
        #remove order from the account of every user that owns one
        order = Order.query.filter_by(name=name).first()
        all_owners = order.owner_profiles()
        
        for owner in all_owners:
            owner.remove_order(order)
        
        #delete order from database
        db.session.delete(order)
        db.session.commit()
        flash('Deletion successful')
        return redirect(url_for('search_order'))
    
    return render_template('delete_order.html', title='Order deletion', form=form)

@app.route('/makeorder', methods=['GET', 'POST'])
@login_required
def add_order():
    form = MakeOrderForm()

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data

        order = Order(name=name, price=price)
        db.session.add(order)
        db.session.commit()

        flash('Order successfully created!')
        return redirect(url_for('homepage'))
    
    return render_template('makeorder.html', title='Order creation', form=form )

@app.route('/searchorder/', methods=['GET', 'POST'])
@login_required
def search_order():
    form = SearchOrderForm()
    all_orders = [f.name for f in Order.query.order_by('name')] #name of item passed into form

    if form.validate_on_submit():
        name = request.form['order-choice']
        return redirect(url_for('edit_order', ordername=name))

    return render_template('searchorder.html', title='Search for Order', orders=all_orders, form=form)

@app.route('/searchprofile/', methods=['GET', 'POST'])
@login_required
def search_profile():
    form = SearchProfileForm()
    all_profiles = [p.username for p in Profile.query.order_by('username')] #value label pairs to pass into form

    if form.validate_on_submit():
        name = request.form['profile-choice']
        return redirect(url_for('manageprofile', profilename=name))

    return render_template('searchprofile.html', title='Search for Profile', profiles=all_profiles, form=form)

@app.route('/editorder/<ordername>/', methods=['GET', 'POST'])
@login_required
def edit_order(ordername):
    order = Order.query.filter_by(name=ordername).first()
    form = EditOrderForm(ordername)

    if form.validate_on_submit():
        order.name = form.newname.data
        order.price = form.cost.data
        db.session.commit()
        flash('Entry has been updated')
        return redirect(url_for('edit_order', ordername=form.newname.data))

    elif request.method == 'GET':
        form.newname.data = order.name
        form.cost.data = order.price
        
    return render_template('editorder.html', title='Edit Order', form=form, name=ordername)

@app.route('/manageprofile/<profilename>/', methods=['GET', 'POST'])
@login_required
def manageprofile(profilename):

    #TODO: render all of the profile's fumos inside of a table, display their total price

    profile = Profile.query.filter_by(username=profilename).first()
    if profile is None:
        flash('Profile not found')
        return redirect(url_for('homepage'))

    form = OrderProfileForm(profile)

    all_orders = [f.name for f in Order.query.order_by('name').all()] + ['Leave Blank']
    form.add_order.choices = all_orders

    obj_orders = profile.owned_orders().all()
    owned_orders = [f.name for f in obj_orders] + ['Leave Blank']
    form.remove_order.choices = owned_orders

    if form.validate_on_submit():
        #fumo user wants to add
        ordername = form.add_order.data
        #fumo user wants to remove
        removename = form.remove_order.data
        
        #filled in options each
        if ordername != 'Leave Blank':
            addedorder = Order.query.filter_by(name=ordername).first()
            profile.add_order(addedorder)
            flash('Order has been successfully added to profile')
            db.session.commit()
    
        if removename != 'Leave Blank':
            removedorder = Order.query.filter_by(name=removename).first()
            profile.remove_order(removedorder)
            flash('Order has successfully been removed from profile')
            db.session.commit()

        return redirect(url_for('manageprofile', profilename=profilename))
    
    elif request.method == 'GET':
        form.add_order.data = 'Leave Blank'
        form.remove_order.data = 'Leave Blank'

    return render_template('manageprofile.html', title='Add Order To Profile', orders= obj_orders, form=form)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))


