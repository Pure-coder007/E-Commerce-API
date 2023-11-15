from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from flask_bcrypt import Bcrypt
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import random
from models import get_admin, get_customer, add_admin, add_customer, add_your_products
from database import config
from products import products



app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager()
auth = Blueprint('auth', __name__)
app.config.from_pyfile('config.py')

# Create app
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'language007'
    app.register_blueprint(auth, url_prefix='/auth/v1')
    jwt.init_app(app)
    return app



# Checking if email exists for customers
def email_exists(email):
    customer = get_customer(email)
    return customer is not None



def email_exists_admin(email):
    admin = get_admin(email)
    return admin is not None



# Registering an admin
@auth.route('/register_admin', methods=['POST'])
def register_admin():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    password = data['password']
    if email_exists_admin(email):
        return jsonify ({'message' : 'Email already exists'}), 400
    password_hash = sha256.hash(password)
    add_admin(first_name, last_name, email, password_hash)
    print({
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    })
    return jsonify({'message' : 'Admin registered successfully!'}), 201



# Register customer
@auth.route('/register_customer', methods=['POST'])
def register_customer():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    password = data['password']
    wallet_balance = data.get('wallet_balance', 0)


    if email_exists(email):
        return jsonify ({'message': 'Email already exists'}), 400
    password_hash = sha256.hash(password)
    print("hashed pSSWORD", password_hash)
    add_customer(first_name, last_name, email, password_hash, wallet_balance)
    print({
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    })
    return ({'message' : 'Customer is registered successfully!'})



# Login customer
@auth.route('/login_customer', methods=['POST'])
def login_customer():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'Missing JSON in request', 'status': 400}), 400
    email = data['email']
    password = data['password']

    if not email or not password:
        return jsonify({'message' : 'Missing email or password', 'status':400}), 400
    
    customer = get_customer(email)
    print('Stored Password:', customer['password'])
    if customer and sha256.verify(password, customer['password']):
        access_token = create_access_token(identity=customer['id'])
        print('Login successful')
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'status': 200
        }), 200
    else:
        print('Stored Password:', customer['password'])
        print('Input Password:', password)
        print('Hash Match:', bcrypt.check_password_hash(customer['password'], password))
        return jsonify({'message': 'Invalid password ', 'status': 400}), 400



# Customer wallet top-up
@auth.route('/top_up/<int:id>', methods=['PUT'])
@jwt_required()
def top_up(id):
    user_id = get_jwt_identity()
    if user_id is None:
        return jsonify({'message': 'User not found'}), 404


    connection = mysql.connector.connect(**config)
    
    
    cursor = connection.cursor()

    query = "SELECT id FROM customers WHERE id = %s"
    cursor.execute(query, (id,))
    customer = cursor.fetchone()
    if customer and customer[0] == user_id:
        wallet_balance = request.json.get('wallet_balance')
        print('nnnnnnnnnn', wallet_balance)

        if wallet_balance is not None:
            query = "UPDATE customers SET wallet_balance = %s WHERE id = %s"
            cursor.execute(query, (wallet_balance, id))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'message': 'Wallet updated successfully', 'status': 200}), 200
        else:
            cursor.close()
            connection.close()
            return jsonify({'message': 'Not successful'}), 401

    cursor.close()
    connection.close()
    return jsonify({'message': 'Customer is not authorized to update this wallet'}, 401)



@auth.route('/get_products', methods=['GET'])
@jwt_required()
def get_products():
    print(products)
    return jsonify ({'Available products': products})





# Adding products to cart

@auth.route('/add_products', methods=['POST'])
@jwt_required()
def add_products():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        if user_id is None:
            return jsonify({'message': 'User not found', 'status': 400}), 400

        name = data.get('name')
        quantity = data.get('quantity')
        price = data.get('price')

        if not name or not quantity or not price:
            return jsonify({'message': 'All fields are required', 'status': 400}), 400

        connection = mysql.connector.connect(**config)

        try:
            with connection.cursor() as cursor:
                check_query = "SELECT * FROM selected_products WHERE name = %s"
                cursor.execute(check_query, (name,))
                existing_product = cursor.fetchone()

                if existing_product:
                    update_query = "UPDATE selected_products SET quantity = quantity + 1 WHERE name = %s"
                    cursor.execute(update_query, (name,))
                else:
                    add_your_products(name, quantity, price, user_id)

            connection.commit()

        except mysql.connector.Error as e:
            connection.rollback()
            return jsonify({'message': f'Database error: {e}', 'status': 500}), 500

        finally:
            connection.close()

        print('name:', name, quantity, price)
        return jsonify({'message': 'Item added successfully!'})

    except Exception as e:
        return jsonify({'message': f'Internal server error: {e}', 'status': 500}), 500





@auth.route('/view_cart', methods=['GET'])
@jwt_required()
def view_cart():
    user_id = get_jwt_identity()

    if user_id is None:
        return jsonify({'message': 'User not found', 'status': 400}), 400

    try:
        connection = mysql.connector.connect(**config)
        with connection.cursor() as cursor:
            # Retrieve selected products in the cart for the user
            view_cart_query = """
                SELECT id, name, quantity, price
                FROM selected_products
                WHERE customer_id = %s
            """
            cursor.execute(view_cart_query, (user_id,))
            cart_products = cursor.fetchall()

            if not cart_products:
                return jsonify({'message': 'Your cart is empty', 'status': 200, 'cart': []}), 200

            # Convert the result to a list of dictionaries for JSON response
            cart_list = [{'id': product[0], 'name': product[1], 'quantity': product[2], 'price': product[3]} for product in cart_products]

        return jsonify({'message': 'Cart retrieved successfully', 'status': 200, 'cart': cart_list}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'message': 'Internal Server Error', 'status': 500}), 500

    finally:
        if connection.is_connected():
            connection.close()






# Remove products from cart
@auth.route('/delete_product', methods=['DELETE'])
@jwt_required()
def delete_product():
    user_id = get_jwt_identity()
    data = request.get_json()

    if user_id is None:
        return jsonify({'message': 'User not found', 'status': 400}), 400

    name = data.get('name') 

    if name is None:
        return jsonify({'message': 'Item not found', 'status': 400}), 400

    try:
        connection = mysql.connector.connect(**config)
        with connection.cursor() as cursor:
            # Check if the product exists for the user before deleting
            check_query = "SELECT * FROM selected_products WHERE name = %s AND customer_id = %s"
            cursor.execute(check_query, (name, user_id))
            product = cursor.fetchone()

            if product is None:
                return jsonify({'message': 'Item not found for the user', 'status': 404}), 404

            delete_query = "DELETE FROM selected_products WHERE name = %s AND customer_id = %s"
            cursor.execute(delete_query, (name, user_id))
        
        connection.commit()
        return jsonify({'message': 'Item deleted successfully', 'status': 200}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'message': 'Internal Server Error', 'status': 500}), 500

    finally:
        if connection.is_connected():
            connection.close()



# Paying for product
@auth.route('/payment', methods=['POST'])
@jwt_required()
def payment():
    user_id = get_jwt_identity()
    data = request.get_json()
    check_out = data.get('check_out')

    if user_id is None:
        return jsonify({'message': 'User not found', 'status': 400}), 400

    try:
        connection = mysql.connector.connect(**config)
        with connection.cursor() as cursor:
            # Check if the user has any products in the cart
            check_cart_query = "SELECT COUNT(*) FROM selected_products WHERE customer_id = %s"
            cursor.execute(check_cart_query, (user_id,))
            cart_count = cursor.fetchone()[0]

            if cart_count == 0:
                return jsonify({'message': 'Your cart is empty. Add products before checkout.', 'status': 400}), 400

            # Continue with the payment process
            get_balance_query = "SELECT wallet_balance FROM customers WHERE id = %s"
            cursor.execute(get_balance_query, (user_id,))
            wallet_balance = cursor.fetchone()[0]

            get_total_amount_query = "SELECT SUM(quantity * price) FROM selected_products WHERE customer_id = %s"
            cursor.execute(get_total_amount_query, (user_id,))
            total_amount = cursor.fetchone()[0]

            if wallet_balance < total_amount:
                return jsonify({'message': 'Insufficient wallet balance', 'status': 400}), 400

            new_balance = wallet_balance - total_amount
            update_balance_query = "UPDATE customers SET wallet_balance = %s WHERE id = %s"
            cursor.execute(update_balance_query, (new_balance, user_id))

            delete_paid_products_query = "DELETE FROM selected_products WHERE customer_id = %s"
            cursor.execute(delete_paid_products_query, (user_id,))

        connection.commit()
        return jsonify({'message': 'Payment successful', 'status': 200, 'new_balance': new_balance}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'message': 'Internal Server Error', 'status': 500}), 500

    finally:
        if connection.is_connected():
            connection.close()
