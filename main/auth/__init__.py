from flask import Blueprint

bp = Blueprint('auth', __name__)

from main.auth import forms, routes