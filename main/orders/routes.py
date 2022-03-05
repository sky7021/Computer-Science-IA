from main import db
from main.orders import bp
from flask import render_template, redirect, url_for, request, flash, request
from main.orders.forms import EditOrderForm, EmptyForm, MakeOrderForm, SearchOrderForm
from flask_login import login_required
from main.models import Order

@bp.route('/deleteorder/<name>', methods=['POST'])
@login_required
def delete_order(name):
    form = EmptyForm()

    if form.validate_on_submit():
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
        return redirect(url_for('auth.homepage'))
    
    return render_template('orders/makeorder.html', title='Order creation', form=form )

@bp.route('/searchorder/', methods=['GET', 'POST'])
@login_required
def search_order():
    form = SearchOrderForm()
    all_orders = [f.name for f in Order.query.order_by('name')] #name of item passed into form

    if form.validate_on_submit():
        name = request.form['order-choice']
        print(type(name))
        if name != '':
            return redirect(url_for('orders.edit_order', ordername=name))
        else:
            flash('Field cannot be blank')
            return redirect(url_for('orders.search_order'))

    return render_template('orders/searchorder.html', title='Search for Order', orders=all_orders, form=form)

@bp.route('/editorder/<ordername>/', methods=['GET', 'POST'])
@login_required
def edit_order(ordername):
    order = Order.query.filter_by(name=ordername).first()
    if order is None:
        flash('Item not found')
        return redirect(url_for('auth.homepage')) #maybe need to import auth blueprint as a reference
        
    form = EditOrderForm(order)
    delete_form = EmptyForm()

    if form.validate_on_submit():
        order.name = form.newname.data
        order.price = form.cost.data
        db.session.commit()
        flash('Entry has been updated')
        return redirect(url_for('orders.edit_order', ordername=form.newname.data))

    elif request.method == 'GET':
        form.newname.data = order.name
        form.cost.data = order.price
        
    return render_template('orders/editorder.html', title='Edit Order', form=form, delete_form=delete_form,
    name=ordername)