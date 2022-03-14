from flask import Blueprint 

bp = Blueprint('auth', __name__) #creates blueprint object named 'auth' and current file (__name__)

from main.auth import forms, routes #initializes files within blueprint folder after initialization 