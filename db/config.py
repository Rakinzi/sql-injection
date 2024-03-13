import sqlite3
import datetime
from flask import Flask, render_template, flash
import socket


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('db/traffic.db')

    def check_user(self):
        ipaddress = socket.gethostbyname(socket.gethostname())
        hostname = socket.gethostname()
        cursor = self.conn.cursor()
        query = f"SELECT * FROM traffic_users WHERE ip_address = '{ipaddress}' AND host_name = '{hostname}' AND strikes = {3}"
        if cursor.execute(query):
            rows = cursor.fetchall()
            num_rows = len(rows)
            if num_rows > 0:
                return 1
            else:
                return 0
        else:
            return 0

    def insert_malicious_users(self, detail):
        cursor = self.conn.cursor()
        status = 'not blocked'
        time = datetime.datetime.now()
        query = f"INSERT INTO traffic_users (ip_address, status, date_time, strikes, host_name) VALUES ('{detail['ip_address']}', '{status}', '{time}', {1}, '{detail['host_name']}' )"
        cursor.execute(query)
        self.conn.commit()
        self.conn.close()

    def login_users(self, user_details):
        cursor = self.conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{user_details['username']}' AND password = '{user_details['password']}'"
        if cursor.execute(query):
            rows = cursor.fetchall()
            num_rows = len(rows)
            if (num_rows > 0):
                print("Access Granted")
                self.conn.close()
                return 'Logged In'
            else:
                self.conn.close()
                print('Access Denied')
                return "Access Denied"


    def check_strikes(self, details):
        cursor = self.conn.cursor()
        query = f"SELECT * FROM traffic_users WHERE ip_address = '{details['ip_address']}' AND host_name = '{details['host_name']}'"
        if cursor.execute(query):
            rows = cursor.fetchall()
            num_rows = len(rows)
            if num_rows == 0:
                self.insert_malicious_users(detail=details)
                return 'Not Blocked'
            else:
                strikes = int(rows[0][3])
                if strikes == 2:
                    status = 'blocked'
                    query = f"UPDATE traffic_users SET strikes = {3}, status = '{status}'  WHERE ip_address = '{details['ip_address']}' AND host_name = '{details['host_name']}'"
                    cursor.execute(query)
                    self.conn.commit()
                    self.conn.close()
                    return 'Blocked'
                else:
                    strikes += 1
                    status = 'not blocked'
                    query = f"UPDATE traffic_users SET strikes = {strikes}, status = '{status}'  WHERE ip_address = '{details['ip_address']}' AND host_name = '{details['host_name']}'"
                    cursor.execute(query)
                    self.conn.commit()
                    self.conn.close()
                    return "Not blocked"

    def register_users(self, register_details):
        """
        This method registers users to the database and closes the connection
        """
        cursor = self.conn.cursor()
        query = f"INSERT INTO users (username, password, email) VALUES ('{register_details['username']}', '{register_details['password']}', '{register_details['email']}')"
        if cursor.execute(query):
            self.conn.commit()
            self.conn.close()
            print("BHOO")
            return "Success"
        else:
            print("MA1")
            return "Failed to Register users"
