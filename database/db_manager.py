import sqlite3


class DBManager:

    def __init__(self):

        self.conn = sqlite3.connect("bom_index.db")
        self.cursor = self.conn.cursor()

        self.create_table()

    # --------------------------------------------------
    # Create database tables
    # --------------------------------------------------
    def create_table(self):

        # BOM data table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS bom_data(

        file TEXT,
        row INTEGER,

        assembly TEXT,
        model TEXT,
        manufacturer TEXT,
        part TEXT,
        spec TEXT,

        qty_rig TEXT,
        rigs TEXT,
        qty_procure TEXT,

        price TEXT,
        quote_lead TEXT,
        nego_lead TEXT,

        supplier TEXT,

        pr_date TEXT,
        pr_no TEXT,

        po_release_date TEXT,
        po_no TEXT,
        po_date TEXT,
        estimated_receive TEXT,
        received_qty TEXT,
        invoice_no TEXT,
        status TEXT

        )
        """)

        # table storing loaded BOM file paths
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS loaded_files(
        file_path TEXT PRIMARY KEY
        )
        """)

        self.conn.commit()

    # --------------------------------------------------
    # Insert BOM row
    # --------------------------------------------------
    def insert(self, record):

        self.cursor.execute("""
        INSERT INTO bom_data VALUES(
        ?,?,?,?,?,?,?,?,?,?,
        ?,?,?,?,?,?,?,?,?,?,
        ?,?,?
        )
        """, record)

    # --------------------------------------------------
    # Commit changes
    # --------------------------------------------------
    def commit(self):
        self.conn.commit()

    # --------------------------------------------------
    # Delete previous records of a BOM file
    # (prevents duplicates when reloading BOM)
    # --------------------------------------------------
    def delete_file_records(self, file_path):

        self.cursor.execute(
            "DELETE FROM bom_data WHERE file = ?",
            (file_path,)
        )

        self.conn.commit()

    # --------------------------------------------------
    # Search BOM records
    # --------------------------------------------------
    def search(self, keyword):

        keyword = f"%{keyword.lower()}%"

        self.cursor.execute("""
        SELECT * FROM bom_data
        WHERE
        lower(assembly) LIKE ?
        OR lower(model) LIKE ?
        OR lower(manufacturer) LIKE ?
        OR lower(part) LIKE ?
        OR lower(spec) LIKE ?
        OR lower(supplier) LIKE ?
        """,
        (keyword, keyword, keyword, keyword, keyword, keyword))

        return self.cursor.fetchall()

    # --------------------------------------------------
    # Save loaded BOM file
    # --------------------------------------------------
    def add_loaded_file(self, file_path):

        self.cursor.execute(
            "INSERT OR IGNORE INTO loaded_files VALUES (?)",
            (file_path,)
        )

        self.conn.commit()

    # --------------------------------------------------
    # Get previously loaded BOM files
    # --------------------------------------------------
    def get_loaded_files(self):

        self.cursor.execute("SELECT file_path FROM loaded_files")

        rows = self.cursor.fetchall()

        return [r[0] for r in rows]

    # --------------------------------------------------
    # Optional: clear database (debug/reset)
    # --------------------------------------------------
    def clear_all(self):

        self.cursor.execute("DELETE FROM bom_data")
        self.cursor.execute("DELETE FROM loaded_files")

        self.conn.commit()
