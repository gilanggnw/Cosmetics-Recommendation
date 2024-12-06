from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS
import os

# Set up Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Read CSV file once when the app starts (ensure the path is correct for Vercel)
try:
    # Adjust path to point to the right location (Vercel serverless functions)
    df = pd.read_csv(os.path.join(os.getcwd(), 'flask_backend', 'cosmetic_p.csv'))
    print("CSV file loaded successfully")
except Exception as e:
    print(f"Error loading CSV file: {e}")
    df = None

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

# Simple hello world endpoint
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello from Flask!")

# For Vercel deployment, this is the handler for serverless functions
def handler(request):
    return app(request)
