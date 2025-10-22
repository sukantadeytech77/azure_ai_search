
import psycopg2

def store_metadata(doc_id, filename, upload_time, connection_params):
    conn = psycopg2.connect(**connection_params)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO documents (doc_id, filename, upload_time)
        VALUES (%s, %s, %s)
    """, (doc_id, filename, upload_time))
    conn.commit()
    cur.close()
    conn.close()
