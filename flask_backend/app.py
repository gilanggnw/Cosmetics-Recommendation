from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Read CSV file once when the app starts
try:
    df = pd.read_csv('../cosmetic_p.csv')
    print("CSV file loaded successfully")
except Exception as e:
    print(f"Error loading CSV file: {e}")
    df = None

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
    
@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    if df is not None:
        product = df.iloc[id].to_dict() if id < len(df) else None
        if product:
            return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello from Flask!")

if __name__ == '__main__':
    app.run(debug=True)