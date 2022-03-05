from flask import Blueprint

bp = Blueprint('orders', __name__)

from main.orders import routes, forms