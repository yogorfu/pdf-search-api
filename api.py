from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable API access

DB_FILE = "knowledge_base.db"

def search_database(query):
    """Search the database for relevant content."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Search for query within document content
    cursor.execute("SELECT filename, url, content FROM documents WHERE content LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()
    
    conn.close()
    return results

@app.route('/query', methods=['GET'])
def query_database():
    """Handle API requests to search the database."""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({"error": "Query is required."}), 400

    results = search_database(query)

    if not results:
        return jsonify({"answer": "No relevant information found."})

    return jsonify({
        "results": [{"filename": r[0], "url": r[1], "content": r[2][:500] + "..."} for r in results]
    })

if __name__ == '__main__':
    # Changed port to 5001 to avoid conflicts with another process
    app.run(host="0.0.0.0", port=5001, debug=True)
