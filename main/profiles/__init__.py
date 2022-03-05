from flask import Blueprint

bp = Blueprint('profiles', __name__)

from main.profiles import routes, forms