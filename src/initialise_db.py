import os
import sqlite3
import json
import logging
from datetime import datetime

def parse_date(date_str):
    """Convert a date string in 'DD Mon YYYY' format to ISO 'YYYY-MM-DD'."""
    return datetime.strptime(date_str, "%d %b %Y").strftime("%Y-%m-%d")

def parse_percentage(p_str):
    """Convert a percentage string (e.g. '79.4%') to a float; returns None if 'N/A'."""
    if p_str == "N/A":
        return None
    return float(p_str.strip("%"))

def create_tables(conn):
    """Creates tables in the SQLite database with explicit DDL."""
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS terms (
            termName TEXT PRIMARY KEY,
            startDate DATE,
            endDate DATE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            studentId INTEGER PRIMARY KEY,
            name TEXT,
            sex TEXT,
            yearGroup TEXT,
            form TEXT,
            dob DATE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS guardians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            studentId INTEGER,
            name TEXT,
            relationship TEXT,
            email TEXT,
            phone TEXT,
            FOREIGN KEY(studentId) REFERENCES students(studentId)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            studentId INTEGER,
            termName TEXT,
            present REAL,
            authorisedAbsent REAL,
            unauthorisedAbsent REAL,
            late REAL,
            FOREIGN KEY(studentId) REFERENCES students(studentId),
            FOREIGN KEY(termName) REFERENCES terms(termName)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS behaviour (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            studentId INTEGER,
            termName TEXT,
            detentions INTEGER,
            behaviourPoints INTEGER,
            FOREIGN KEY(studentId) REFERENCES students(studentId),
            FOREIGN KEY(termName) REFERENCES terms(termName)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS attainment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            studentId INTEGER,
            termName TEXT,
            english INTEGER,
            maths INTEGER,
            science INTEGER,
            FOREIGN KEY(studentId) REFERENCES students(studentId),
            FOREIGN KEY(termName) REFERENCES terms(termName)
        )
    ''')
    
    conn.commit()

def insert_terms(conn, terms_data):
    """Insert term records into the terms table."""
    c = conn.cursor()
    for term in terms_data:
        c.execute('''
            INSERT INTO terms (termName, startDate, endDate)
            VALUES (?, ?, ?)
        ''', (term["termName"], parse_date(term["startDate"]), parse_date(term["endDate"])))
    conn.commit()

def insert_students(conn, students_data):
    """Insert student records into the students table."""
    c = conn.cursor()
    for student in students_data:
        c.execute('''
            INSERT INTO students (studentId, name, sex, yearGroup, form, dob)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student["studentId"], student["name"], student["sex"],
              student["yearGroup"], student["form"], parse_date(student["dob"])))
    conn.commit()

def insert_guardians(conn, guardians_data):
    """Insert guardian records into the guardians table."""
    c = conn.cursor()
    for guardian_item in guardians_data:
        student_id = guardian_item["studentId"]
        for guardian in guardian_item["guardiansData"]:
            c.execute('''
                INSERT INTO guardians (studentId, name, relationship, email, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, guardian["name"], guardian["relationship"],
                  guardian["email"], guardian["phone"]))
    conn.commit()

def insert_attendance(conn, attendance_data):
    """Insert attendance records into the attendance table."""
    c = conn.cursor()
    for attendance_item in attendance_data:
        student_id = attendance_item["studentId"]
        for record in attendance_item["termsAttendanceData"]:
            c.execute('''
                INSERT INTO attendance (studentId, termName, present, authorisedAbsent, unauthorisedAbsent, late)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, record["termName"],
                  parse_percentage(record["present"]),
                  parse_percentage(record["authorisedAbsent"]),
                  parse_percentage(record["unauthorisedAbsent"]),
                  parse_percentage(record["late"])))
    conn.commit()

def insert_behaviour(conn, behaviour_data):
    """Insert behaviour records into the behaviour table."""
    c = conn.cursor()
    for behaviour_item in behaviour_data:
        student_id = behaviour_item["studentId"]
        for record in behaviour_item["termsBehaviourData"]:
            c.execute('''
                INSERT INTO behaviour (studentId, termName, detentions, behaviourPoints)
                VALUES (?, ?, ?, ?)
            ''', (student_id, record["termName"], record["detentions"], record["behaviourPoints"]))
    conn.commit()

def insert_attainment(conn, attainment_data):
    """Insert attainment records into the attainment table."""
    c = conn.cursor()
    for attainment_item in attainment_data:
        student_id = attainment_item["studentId"]
        for record in attainment_item["termsAttainmentData"]:
            c.execute('''
                INSERT INTO attainment (studentId, termName, english, maths, science)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, record["termName"], record["english"], record["maths"], record["science"]))
    conn.commit()

def main():
    # Get the absolute path to the directory where this script resides.
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Compute the project base directory (one level up from 'src')
    project_dir = os.path.abspath(os.path.join(script_dir, '..'))
    
    # Set up logging to init_db.log in the project root.
    log_file = os.path.join(project_dir, 'init_db.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting database initialisation.")
    
    # Build paths to the data folder and the database folder.
    data_dir = os.path.join(project_dir, 'data')
    json_file = os.path.join(data_dir, 'school_dummy_data.json')
    db_folder = os.path.join(data_dir, 'db')
    
    # Ensure the database folder exists; create it if needed.
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        logger.info("Created database folder at %s", db_folder)
    
    db_file = os.path.join(db_folder, 'school.db')
    
    # Overwrite the database: remove the file if it exists.
    if os.path.exists(db_file):
        os.remove(db_file)
        logger.info("Removed existing database file at %s", db_file)
    
    # Load JSON data from file.
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        logger.info("Loaded JSON data from %s", json_file)
    except Exception as e:
        logger.error("Error reading JSON file: %s", e)
        raise
    
    # Connect to SQLite database (it will be created fresh).
    try:
        conn = sqlite3.connect(db_file)
        logger.info("Connected to database at %s", db_file)
    except Exception as e:
        logger.error("Error connecting to database: %s", e)
        raise
    
    try:
        # Create tables and insert data.
        create_tables(conn)
        logger.info("Created database tables.")
        
        insert_terms(conn, data["terms"])
        logger.info("Inserted terms data.")
        
        insert_students(conn, data["students"])
        logger.info("Inserted students data.")
        
        insert_guardians(conn, data["guardians"])
        logger.info("Inserted guardians data.")
        
        insert_attendance(conn, data["attendance"])
        logger.info("Inserted attendance data.")
        
        insert_behaviour(conn, data["behaviour"])
        logger.info("Inserted behaviour data.")
        
        insert_attainment(conn, data["attainment"])
        logger.info("Inserted attainment data.")
    except Exception as e:
        logger.error("Error during database initialisation: %s", e)
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
    
    print("Database initialised successfully.")
    logger.info("Database initialised successfully.")

if __name__ == '__main__':
    main()
