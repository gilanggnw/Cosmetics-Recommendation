from flask import Flask, jsonify
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from flask_cors import CORS
import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Set up Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)
csv_path = os.path.join(base_dir, 'cosmetic_p.csv')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'db': os.getenv('DB_NAME'),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor,
    'connect_timeout': 10,
    'read_timeout': 10,
    'write_timeout': 10
}

def get_db_connection():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create search_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    search_query VARCHAR(255) NOT NULL,
                    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Create bookmarks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    product_id INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_bookmark (user_id, product_id)
                )
            """)

        connection.commit()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
    finally:
        connection.close()

# Add this to ensure tables are created when app starts
init_db()

# Read CSV file once when the app starts (ensure the path is correct for Vercel)
try:
    df = pd.read_csv(csv_path)
    print(f"CSV file loaded successfully from {csv_path}")
except Exception as e:
    print(f"Error loading CSV file: {e}")
    df = None

# Add a test endpoint to verify database connection
@app.route('/api/db-test', methods=['GET'])
def test_db():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        connection.close()
        return jsonify({"status": "Database connection successful", "result": result})
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

# API to get all products
@app.route('/api/products', methods=['GET'])
def get_products():
    if df is not None:
        # Add index as id
        df_with_id = df.reset_index()
        df_with_id = df_with_id.rename(columns={'index': 'id'})
        products = df_with_id.to_dict('records')
        return jsonify(products)
    else:
        return jsonify({"error": "Data not available"}), 500
    
# API to get a single product by ID
@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    if df is not None:
        product = df.iloc[id].to_dict() if id < len(df) else None
        if product:
            return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

# Add new API endpoints for user management
@app.route('/api/user/register', methods=['POST'])
def register_user():
    try:
        connection = get_db_connection()
        data = request.json
        
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(sql, (data['username'], data['email'], data['password_hash']))
        
        connection.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

# Add bookmark endpoint
@app.route('/api/bookmark', methods=['POST'])
def add_bookmark():
    try:
        connection = get_db_connection()
        data = request.json
        
        with connection.cursor() as cursor:
            sql = "INSERT INTO bookmarks (user_id, product_id) VALUES (%s, %s)"
            cursor.execute(sql, (data['user_id'], data['product_id']))
        
        connection.commit()
        return jsonify({"message": "Bookmark added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

# Add search history endpoint
@app.route('/api/search/history', methods=['POST'])
def add_search_history():
    try:
        connection = get_db_connection()
        data = request.json
        
        with connection.cursor() as cursor:
            sql = "INSERT INTO search_history (user_id, search_query) VALUES (%s, %s)"
            cursor.execute(sql, (data['user_id'], data['search_query']))
        
        connection.commit()
        return jsonify({"message": "Search history recorded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

# Simple hello world endpoint
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello from Flask!")

# For Vercel deployment, this is the handler for serverless functions
def handler(request):
    return app(request)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
