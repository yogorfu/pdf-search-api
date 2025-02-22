from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # Enable API access

DB_FILE = "knowledge_base.db"

# A simple set of stopwords to filter out less important words
STOPWORDS = {"cases", "that", "deal", "with", "and", "the", "of", "for", "in", "a", "an"}

def ensure_fts_table():
    """
    Checks if the FTS virtual table 'documents_fts' exists.
    If it doesn't, creates it and populates it from the 'documents' table.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Try a simple query to see if the FTS table exists
        cursor.execute("SELECT count(*) FROM documents_fts")
        print("FTS table exists.")
    except sqlite3.OperationalError:
        print("FTS table 'documents_fts' not found. Creating now...")
        # Create the FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE documents_fts USING fts5(
                filename,
                url,
                content
            )
        """)
        # Populate the FTS table from the existing documents table
        cursor.execute("""
            INSERT INTO documents_fts (filename, url, content)
            SELECT filename, url, content FROM documents
        """)
        conn.commit()
        print("FTS table 'documents_fts' created and populated successfully.")
    finally:
        conn.close()

def extract_keywords(query):
    """
    Tokenizes the query, removes stopwords, and returns a string suitable for FTS MATCH.
    For example, "cases that deal with air force rotc and adhd" becomes "air OR force OR rotc OR adhd".
    """
    tokens = re.findall(r'\w+', query.lower())
    keywords = [token for token in tokens if token not in STOPWORDS]
    # Join tokens using OR so that any matching keyword can be returned
    return " OR ".join(keywords)

def search_database(query):
    """
    Uses the extracted keywords to search the FTS virtual table.
    Make sure you've created an FTS table (e.g., documents_fts) that indexes filename, url, and content.
    """
    fts_query = extract_keywords(query)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Execute a MATCH query on the FTS table
    cursor.execute("SELECT filename, url, content FROM documents_fts WHERE documents_fts MATCH ?", (fts_query,))
    results = cursor.fetchall()
    conn.close()
    return results

@app.route('/query', methods=['GET'])
def query_database():
    user_query = request.args.get('q', '').strip()
    if not user_query:
        return jsonify({"error": "Query is required."}), 400

    results = search_database(user_query)
    if not results:
        return jsonify({"answer": "No relevant information found."})

    # Return full document text for each matching result
    return jsonify({
        "results": [
            {"filename": r[0], "url": r[1], "content": r[2]}
            for r in results
        ]
    })

if __name__ == '__main__':
    # Ensure FTS table exists before running the app
    ensure_fts_table()
    # Running on port 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
