#not a file; initialized in init, part of folder
from main import db, create_app
from main.models import Admin, Profile, LinkOrder, Order

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Admin': Admin, 'Profile': Profile, 'Order': Order, 'LinkOrder': LinkOrder}