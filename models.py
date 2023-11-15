import mysql.connector
from database import config
from datetime import datetime
from mysql.connector import Error
from products import products


class User():
    def __init__(self, id, first_name, last_name, email, password, wallet_balance):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.wallet_balance = wallet_balance

    @classmethod
    def get(cls, user_id):
        pass


def add_admin(first_name, last_name, email, password):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "INSERT INTO admin (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (first_name, last_name, email, password))
    connection.commit()
    cursor.close()
    connection.close()
    return True


def add_customer(first_name, last_name, email, password, wallet_balance):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "INSERT INTO customers (first_name, last_name, email, password, wallet_balance) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (first_name, last_name, email, password, wallet_balance))
    connection.commit()
    cursor.close()
    connection.close()
    return True


def get_customer(email):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM customers WHERE email = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result


def get_admin(email):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(buffered=True)
    query = "SELECT * FROM admin WHERE email = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result


def add_your_products(name, quantity, price, customer_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "INSERT INTO selected_products (name, quantity, price, customer_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, quantity, price, customer_id))
    connection.commit()
    cursor.close()
    connection.close()