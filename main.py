from flask import Flask, render_template, request, redirect, url_for, flash
from models import model
from db import config
import socket


app = Flask(__name__)


@app.route('/')
def index():
    db_insert = config.Database()
    if db_insert.check_user() == 0:
        return render_template('index.html')
    else:
        return render_template('404.html')


@app.route('/check-sqli', methods=['POST'])
def check_sqli():
    db_insert = config.Database()
    form_items = {}
    for key, value in request.form.items():
        form_items[key] = value
    details = {
        "host_name": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname())
    }
    clf = model.Model()
    prediction = clf.make_predictions(form_items.values())
    if prediction == 1:
       if db_insert.check_strikes(details=details) == 'Blocked':
            return redirect(url_for('index'))
       else:
            return redirect(url_for('index'))
    else:
        if db_insert.login_users(form_items) == 'Logged In':
            return redirect(url_for('user'))
        else:
            return redirect(url_for('index'))

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/user')
def user():
    db_insert = config.Database()
    if db_insert.check_user() == 0:
        return render_template('user-dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
