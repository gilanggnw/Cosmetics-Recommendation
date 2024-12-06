from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_cors import CORS
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
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],  # Add your Vue.js development server
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Setup JWT using only environment variable
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
if not app.config['JWT_SECRET_KEY']:
    raise ValueError("No JWT_SECRET_KEY set for Flask application")
    
jwt = JWTManager(app)

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)
csv_path = os.path.join(base_dir, 'api/cosmetic_p.csv')

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
        
        # Hash the password before storing
        password_hash = generate_password_hash(data['password_hash'])
        
        with connection.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", 
                         (data['email'], data['username']))
            if cursor.fetchone():
                return jsonify({"error": "Email or username already exists"}), 400
                
            # Insert new user
            sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(sql, (data['username'], data['email'], password_hash))
            
            # Get the new user's ID
            user_id = cursor.lastrowid
            
        connection.commit()
        
        # Generate JWT token
        token = create_access_token(identity=user_id)
        
        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": {
                "username": data['username'],
                "email": data['email']
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/login', methods=['POST'])
def login():
    try:
        connection = get_db_connection()
        data = request.json
        
        with connection.cursor() as cursor:
            # Find user by email
            cursor.execute("SELECT id, username, email, password_hash FROM users WHERE email = %s", 
                         (data['email'],))
            user = cursor.fetchone()
            
            if user is None:
                return jsonify({"error": "Invalid email or password"}), 401
            
            # Verify password
            if check_password_hash(user['password_hash'], data['password']):
                # Generate access token
                access_token = create_access_token(identity=user['id'])
                
                return jsonify({
                    "token": access_token,
                    "user": {
                        "id": user['id'],
                        "username": user['username'],
                        "email": user['email']
                    }
                })
            else:
                return jsonify({"error": "Invalid email or password"}), 401
                
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500
    finally:
        if connection:
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

# Update the search history endpoint to properly handle CORS
@app.route('/api/search/history', methods=['POST', 'OPTIONS'])
@jwt_required()
def add_search_history():
    if request.method == 'OPTIONS':
        return jsonify({"message": "OK"}), 200
        
    try:
        current_user_id = get_jwt_identity()  # Get user ID from JWT token
        data = request.json
        
        if not data or 'search_query' not in data:
            return jsonify({"error": "Missing search query"}), 422
            
        connection = get_db_connection()
        
        with connection.cursor() as cursor:
            sql = "INSERT INTO search_history (user_id, search_query) VALUES (%s, %s)"
            cursor.execute(sql, (current_user_id, data['search_query']))
            
        connection.commit()
        return jsonify({"message": "Search history recorded"}), 201
        
    except Exception as e:
        print(f"Search history error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

# Simple hello world endpoint
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello from Flask!")

if __name__ == '__main__':
    app.run(debug=True)
else:
    # This is needed for Vercel serverless deployment
    app = app.wsgi_app

def handler(event, context):
    return app
