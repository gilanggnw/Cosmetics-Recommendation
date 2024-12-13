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
csv_path = os.path.join(current_dir, 'cosmetic_p.csv')  # CSV file should be in the api folder

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

            # Create new search_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    search_query VARCHAR(255) NOT NULL,
                    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
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
            # Create click_counts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS click_counts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    cleanser_count INT NOT NULL,
                    facemask_count INT NOT NULL,
                    eyecream_count INT NOT NULL,
                    moisturizer_count INT NOT NULL,
                    treatment_count INT NOT NULL,
                    sunprotect_count INT NOT NULL,
                    normal_count INT NOT NULL,
                    dry_count INT NOT NULL,
                    sensitive_count INT NOT NULL,
                    oily_count INT NOT NULL,
                    combination_count INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
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
            
            # Create initial click_counts entry for the new user
            cursor.execute("""
                INSERT INTO click_counts 
                (user_id, cleanser_count, facemask_count, eyecream_count, 
                moisturizer_count, treatment_count, sunprotect_count, 
                normal_count, dry_count, sensitive_count, oily_count, 
                combination_count)
                VALUES (%s, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            """, (user_id,))
            
        connection.commit()
        
        # Generate JWT token
        token = create_access_token(identity=user_id)
        
        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": user_id,
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

@app.route('/api/search/history', methods=['POST', 'OPTIONS'])
@jwt_required()
def handle_options():
    response = jsonify({'message': 'OK'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    return response, 200
def add_search_history():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        search_query = data.get('search_query')

        if not user_id or not search_query:
            return jsonify({"error": "Missing user_id or search_query"}), 422

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO search_history (user_id, search_query) VALUES (%s, %s)"
                cursor.execute(sql, (user_id, search_query))
            connection.commit()
            return jsonify({"message": "Search history recorded", "query": search_query}), 201
        finally:
            connection.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/click-count', methods=['POST'])
@jwt_required()
def update_click_count():
    try:
        user_id = get_jwt_identity()
        data = request.json
        filter_type = data.get('filter_type')  # e.g., 'moisturizer', 'oily', etc.

        if not filter_type:
            return jsonify({"error": "Missing filter_type"}), 400

        # Map filter types to column names
        column_mapping = {
            'Cleanser': 'cleanser_count',
            'Face Mask': 'facemask_count',
            'Eye cream': 'eyecream_count',
            'Moisturizer': 'moisturizer_count',
            'Treatment': 'treatment_count',
            'Sun protect': 'sunprotect_count',
            'Normal': 'normal_count',
            'Dry': 'dry_count',
            'Sensitive': 'sensitive_count',
            'Oily': 'oily_count',
            'Combination': 'combination_count'
        }

        column_name = column_mapping.get(filter_type)
        if not column_name:
            return jsonify({"error": "Invalid filter type"}), 400

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Check if user has an entry
            cursor.execute("SELECT * FROM click_counts WHERE user_id = %s", (user_id,))
            user_entry = cursor.fetchone()

            if user_entry:
                # Increment the specific count
                cursor.execute(f"UPDATE click_counts SET {column_name} = {column_name} + 1 WHERE user_id = %s", (user_id,))
            else:
                # Create new entry with all counts set to 0 except the current one
                columns = column_mapping.values()
                default_values = {col: 1 if col == column_name else 0 for col in columns}
                
                sql = """
                    INSERT INTO click_counts 
                    (user_id, cleanser_count, facemask_count, eyecream_count, 
                    moisturizer_count, treatment_count, sunprotect_count, 
                    normal_count, dry_count, sensitive_count, oily_count, 
                    combination_count) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (user_id, 
                         default_values['cleanser_count'],
                         default_values['facemask_count'],
                         default_values['eyecream_count'],
                         default_values['moisturizer_count'],
                         default_values['treatment_count'],
                         default_values['sunprotect_count'],
                         default_values['normal_count'],
                         default_values['dry_count'],
                         default_values['sensitive_count'],
                         default_values['oily_count'],
                         default_values['combination_count'])
                cursor.execute(sql, values)

        connection.commit()
        return jsonify({"message": f"{filter_type} count updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()
            
@app.route('/api/click-counts', methods=['GET'])
@jwt_required()
def get_click_counts():
    try:
        user_id = get_jwt_identity()
        connection = get_db_connection()
        
        with connection.cursor() as cursor:
            # Get user's click counts
            cursor.execute("""
                SELECT * FROM click_counts 
                WHERE user_id = %s
            """, (user_id,))
            
            user_counts = cursor.fetchone()
            
            if not user_counts:
                return jsonify({
                    "error": "No click counts found for user"
                }), 404

            return jsonify(user_counts), 200

    except Exception as e:
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
