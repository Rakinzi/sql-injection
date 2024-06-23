import sqlite3
import datetime
from flask import Flask, render_template, flash, session, redirect, url_for
import socket


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('db/traffic.db')
        self.conn.row_factory = sqlite3.Row  # Setting the row factory

    def check_user(self):
        ipaddress = socket.gethostbyname(socket.gethostname())
        hostname = socket.gethostname()
        cursor = self.conn.cursor()
        query = f"SELECT * FROM traffic_users WHERE ip_address = '{ipaddress}' AND host_name = '{hostname}' AND strikes = {3}"
        if cursor.execute(query):
            rows = cursor.fetchone()
            if rows is not None:
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

    def check_strikes(self, details):
        activity_id = self.insert_activity_with_sqli(details, details['payloads'])
        if activity_id is not None:
            cursor = self.conn.cursor()
            query = f"SELECT * FROM traffic_users WHERE ip_address = '{details['ip_address']}' AND host_name = '{details['host_name']}'"
            if cursor.execute(query):
                rows = cursor.fetchone()
                if rows is None:
                    self.insert_malicious_users(detail=details)
                    status = 'not blocked'
                    flash("Invalid username or password", 'error')
                    return status
                else:
                    strikes = int(rows['strikes'])
                    if strikes == 2:
                        status = 'blocked'
                        query = f"UPDATE traffic_users SET strikes = {3}, status = '{status}'  WHERE ip_address = '{details['ip_address']}' AND host_name = '{details['host_name']}'"
                        cursor.execute(query)
                        self.conn.commit()
                        self.conn.close()
                        return status
                    else:
                        strikes += 1
                        status = 'not blocked'
                        query = f"UPDATE traffic_users SET strikes = {strikes}, status = '{status}'  WHERE ip_address = '{details['ip_address']}' AND host_name = '{details['host_name']}'"
                        cursor.execute(query)
                        self.conn.commit()
                        self.conn.close()
                        flash("Invalid username or password", 'error')
                        return status

    def insert_activity_with_sqli(self, detail, payloads):
        cursor = self.conn.cursor()
        time = datetime.datetime.now()
        query_activity = f"INSERT INTO injection_activity (ip_address, timestamp, host_name, user_agents) VALUES ('{detail['ip_address']}', '{time}', '{detail['host_name']}', '{detail['user_agent']}')"
        cursor.execute(query_activity)
        self.conn.commit()
        activity_id = cursor.lastrowid
        for payload in payloads:
            payload = f"*{payload}*"
            query_sqli = f"INSERT INTO sql_injections (activity_id, sqli_statements) VALUES ({activity_id}, '{payload}')"
            cursor.execute(query_sqli)
        self.conn.commit()
        return activity_id

    def insert_sqli_statements(self, activity_id, statements):
        cursor = self.conn.cursor()
        for statement in statements:
            query = f"INSERT INTO sql_injections (activity_id, sqli_statements) VALUES ({activity_id}, '{statement}')"
            cursor.execute(query)
        self.conn.commit()
        self.conn.close()

    def get_blocked_users(self):
        cursor = self.conn.cursor()
        query = 'SELECT * FROM traffic_users WHERE status = "blocked"'
        cursor.execute(query)
        blocked_users = cursor.fetchall()
        self.conn.close()
        return blocked_users

    def delete_blocked_user(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM traffic_users WHERE id = ?", (user_id,))
            self.conn.commit()
            self.conn.close()
            return True
        except sqlite3.Error as e:
            print("Error deleting blocked user:", e)
            return False

    def get_payloads(self):
        cursor = self.conn.cursor()
        query = 'SELECT * FROM sql_injections'
        cursor.execute(query)
        payloads = cursor.fetchall()
        self.conn.close()
        return payloads

    def get_insert_activity(self):
        cursor = self.conn.cursor()
        query = 'SELECT * FROM injection_activity'
        cursor.execute(query)
        activity = cursor.fetchall()
        self.conn.close()
        return activity
