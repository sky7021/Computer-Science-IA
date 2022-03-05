from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from main import db
from main.profiles import bp
from main.profiles.forms import CreateProfile, SearchProfileForm, OrderProfileForm, EmptyForm
from main.models import Profile, Order

#creates customer profile
@bp.route('/create-profile', methods=['GET', 'POST'])
@login_required
def create_profile():

    form = CreateProfile()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data

        profile = Profile(username=username, email=email)
        db.session.add(profile)
        db.session.commit()

        flash('Profile added')
        return redirect(url_for('profiles.create_profile'))
    
    return render_template('profiles/createprofile.html', title='Create profile', form=form)

@bp.route('/deleteprofile/<id>', methods=['POST'])
@login_required
def delete_profile(id):
    form = EmptyForm()

    if form.validate_on_submit():
        profile = Profile.query.filter_by(id=id).first()
        if profile is None:
            flash(f'There is no profile with id {id}')
            return redirect(url_for('auth.index'))
        
        db.session.delete(profile)
        db.session.commit()
        flash('Deletion successful')
        return redirect(url_for('profiles.search_profile'))
    else:
        return redirect(url_for('auth.homepage'))

@bp.route('/searchprofile/', methods=['GET', 'POST'])
@login_required
def search_profile():
    form = SearchProfileForm()
    all_profiles = [f'{p.email}, {p.username}' for p in Profile.query.order_by('username')] #value label pairs to pass into form

    if form.validate_on_submit():
        choice = request.form['profile-choice']
        email = choice.split(', ')[0]
        if email != '':
            return redirect(url_for('profiles.manageprofile', email=email))
        else: 
            flash('Field cannot be blank')
            return redirect(url_for('profiles.search_profile'))

    return render_template('profiles/searchprofile.html', title='Search for Profile', profiles=all_profiles, form=form)

@bp.route('/manageprofile/<email>/', methods=['GET', 'POST'])
@login_required
def manageprofile(email):

    #TODO: render all of the profile's fumos inside of a table, display their total price

    profile = Profile.query.filter_by(email=email).first()
    if profile is None:
        flash('Profile not found')
        return redirect(url_for('auth.homepage'))

    form = OrderProfileForm(profile)
    delete_form = EmptyForm()

    all_orders = [f.name for f in Order.query.order_by('name').all()] + ['Leave Blank']
    form.add_order.choices = all_orders

    obj_orders = profile.owned_orders().all()
    owned_orders = [f.name for f in obj_orders] + ['Leave Blank']
    form.remove_order.choices = owned_orders

    if form.validate_on_submit():
        ordername = form.add_order.data
        quantity = form.add_quantity.data
        removename = form.remove_order.data
        
        #filled in options each
        if ordername != 'Leave Blank':
            addedorder = Order.query.filter_by(name=ordername).first()

            if profile.owns_order(addedorder):
                profile.modify_order(addedorder, quantity)
                flash('Quantity successfully changed')
                db.session.commit()

            else:
                profile.add_order(addedorder, quantity)
                flash('Order has been successfully added to profile')
                db.session.commit()
    
        if removename != 'Leave Blank':
            removedorder = Order.query.filter_by(name=removename).first()
            profile.remove_order(removedorder)
            flash('Order has successfully been removed from profile')
            db.session.commit()

        return redirect(url_for('profiles.manageprofile', email=email))
    
    elif request.method == 'GET':
        form.add_order.data = 'Leave Blank'
        form.remove_order.data = 'Leave Blank'

    return render_template('profiles/manageprofile.html', title=f'{profile.username}\'s Profile', profile=profile, 
    orders= obj_orders, form=form, round=round, delete_form=delete_form
    )
