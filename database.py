import mysql.connector 
from datetime import datetime

# config = {
#     'user' : 'root',
#     'password': 'language007',
#     'host' : 'localhost',
#     'database': 'e_commerce'
# }


config = {
    'user' : 'ukah2023',
    'password': 'language007',
    'host' : 'db4free.net',
    'database' : 'db_comm'
}

def setup_database():
    config['database'] = None
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INT PRIMARY KEY AUTO_INCREMENT,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email VARCHAR (50) NOT NULL,
        password VARCHAR(50) NOT NULL
    )
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INT PRIMARY KEY AUTO_INCREMENT,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL,
        password VARCHAR(150) NOT NULL,
        wallet_balance BIGINT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT PRIMARY KEY AUTO INCREMENT,
        prod_name VARCHAR(50) NOT NULL,
        price BIGINT NOT NULL
    )
""")
    
    cursor.execute("""
    CREATE TABLE selected_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

""")