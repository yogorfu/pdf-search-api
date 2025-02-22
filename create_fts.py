import sqlite3

DB_FILE = "knowledge_base.db"

def create_fts_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Drop the FTS table if it already exists (optional, for a fresh start)
    cursor.execute("DROP TABLE IF EXISTS documents_fts")
    
    # Create a new FTS5 virtual table indexing filename, url, and content
    cursor.execute("""
        CREATE VIRTUAL TABLE documents_fts USING fts5(
            filename,
            url,
            content
        )
    """)
    
    # Populate the FTS table with data from the documents table
    cursor.execute("""
        INSERT INTO documents_fts (filename, url, content)
        SELECT filename, url, content FROM documents
    """)
    
    conn.commit()
    conn.close()
    print("FTS table 'documents_fts' created and populated successfully.")

if __name__ == '__main__':
    create_fts_table()
