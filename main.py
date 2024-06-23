from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import model
from db import config
import socket
import os
from flask_cors import CORS
from test import SQLInjectionScanner
import re

app = Flask(__name__)
secret_key = os.urandom(32)
secret_key = secret_key.hex()
CORS(app)
app.secret_key = secret_key


@app.route('/')
def index():
    return 'Welcome to the SQL Injection Detection API!'


@app.route('/check-sqli', methods=['POST'])
def check_sqli():
    db_insert = config.Database()
    user_agent = request.headers.get('User-Agent')
    form_items = {}
    data = dict(request.form.items())
    for key, value in request.form.items():
        form_items[key] = value
    clf = model.Model()
    prediction, payloads = clf.make_predictions(form_items.values())
    if prediction == 1:
        details = {
            "payloads": payloads,
            "user_agent": user_agent,
            "host_name": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname())
        }
        status = db_insert.check_strikes(details=details)
        return jsonify({'sql_injection_detected': True, 'status': status, 'request': data})
    else:
        return jsonify({'user_data': form_items, 'sql_injection_detected': False, 'request': data})


@app.route('/get-blocked-users', methods=['POST'])
def get_blocked_users():
    if request.method == 'POST':
        db = config.Database()
        blocked_users = db.get_blocked_users()
        blocked_users_list = [dict(row) for row in blocked_users]
        return jsonify(blocked_users=blocked_users_list)


@app.route('/unblock-user', methods=['POST'])
def unblock_user():
    if request.method == 'POST':
        db = config.Database()
        deleted_id = request.form.get('id')
        result = db.delete_blocked_user(deleted_id)
        if result:
            return jsonify({'message': 'User unblocked'})


@app.route('/get-payloads', methods=['POST'])
def get_payloads():
    if request.method == 'POST':
        db = config.Database()
        payloads = db.get_payloads()
        payloads_list = [dict(row) for row in payloads]
        return jsonify(payloads=payloads_list)


@app.route('/get-insert-activity', methods=['POST'])
def get_insert_activity():
    if request.method == 'POST':
        db = config.Database()
        activity = db.get_insert_activity()
        activity_list = [dict(row) for row in activity]
        db = config.Database()
        blocked_users = db.get_blocked_users()
        blocked_users_list = [dict(row) for row in blocked_users]
        return jsonify(activities=activity_list, blocked_users=blocked_users_list)

@app.route('/check-user', methods = ['POST'])
def check_user():
    if request.method == 'POST':
        db = config.Database()
        user = db.check_user()
        if user:
            return jsonify({'message': 'User blocked', 'blocked': True})
        else:
            return jsonify({'message': 'User not blocked', 'blocked': False})

@app.route('/site-checker', methods = ['POST'])
def site_checker():
    if request.method == 'POST':
        data = request.get_json()
        if 'url' in data:
            url = data['url']
            scanner = SQLInjectionScanner()
            status, forms_scanned, url, error = scanner.sql_injection_scan(url)
            if error:
                return jsonify({'error': True   ,'message': 'Invalid URL'})
            else:
                return jsonify({'status': status, 'forms_scanned': forms_scanned, 'url': url})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
