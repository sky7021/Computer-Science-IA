from main import db
from main.orders import bp
from flask import render_template, redirect, url_for, request, flash, request
from main.orders.forms import EditOrderForm, EmptyForm, MakeOrderForm
from flask_login import login_required
from main.models import Order

#route for deleting orders, only POST protocol since the form is empty
#(no fields to display for user input)
@bp.route('/deleteorder/<name>', methods=['POST'])
@login_required
def delete_order(name):

    #initializes form with only a SubmitField
    form = EmptyForm()

    if form.validate_on_submit():
        #order object to be deleted
        order = Order.query.filter_by(name=name).first()

        #delete order from database
        if order is None:
            flash(f'Item {name} does not exist')
            return redirect(url_for('orders.search_order'))

        db.session.delete(order)
        db.session.commit()
        flash('Deletion successful')
        return redirect(url_for('orders.search_order'))
    else:
        return redirect(url_for('orders.search_order'))

@bp.route('/makeorder', methods=['GET', 'POST'])
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
        return redirect(url_for('orders.add_order'))
    
    return render_template('orders/makeorder.html', title='Order creation', form=form )

@bp.route('/searchorder/', methods=['GET', 'POST'])
@login_required
def search_order():
    form = EmptyForm()
    #name of all orders passed into form as a list sorted by 'name' attribute of Order objects
    all_orders = [f.name for f in Order.query.order_by('name')] 

    if form.validate_on_submit():
        #client-side request object has a value for the 'order-choice' parameter of a submitted HTML form 
        name = request.form['order-choice']
        if name != '':
            #redirects with saved variable
            return redirect(url_for('orders.edit_order', ordername=name))
        else:
            flash('Field cannot be blank')
            return redirect(url_for('orders.search_order'))

    return render_template('orders/searchorder.html', title='Search for Order', orders=all_orders, form=form)

#route accepts ordername variable 
@bp.route('/editorder/<ordername>/', methods=['GET', 'POST'])
@login_required
#URL variable referenced in function parameter of the same name 
def edit_order(ordername):
    #order does not exist
    order = Order.query.filter_by(name=ordername).first()
    if order is None:
        flash('Item not found')
        return redirect(url_for('auth.homepage')) 
    
    #form initialization
    form = EditOrderForm(order)
    delete_form = EmptyForm()
    profiles_list = order.owner_profiles()

    if form.validate_on_submit():
        #updates Order attributes
        order.name = form.newname.data
        order.price = form.cost.data
        db.session.commit()
        flash('Entry has been updated')
        #refreshes the page
        return redirect(url_for('orders.edit_order', ordername=form.newname.data))

    #user recieves information from server
    elif request.method == 'GET':
        #fill in fields with default values
        form.newname.data = order.name
        form.cost.data = order.price
        
    return render_template('orders/editorder.html', title='Edit Order', form=form, delete_form=delete_form,
    name=ordername, profiles_list = profiles_list)