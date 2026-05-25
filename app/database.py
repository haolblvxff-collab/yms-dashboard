import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "yms_data.db")

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table: Lots
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Lots (
            Lot_ID TEXT PRIMARY KEY,
            Product_ID TEXT,
            Start_Time TIMESTAMP,
            End_Time TIMESTAMP,
            Status TEXT DEFAULT 'In Progress'
        )
    ''')
    
    # Table: Measurements (For Trend Chart)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Measurements (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Lot_ID TEXT,
            Timestamp TIMESTAMP,
            Parameter_Name TEXT,
            Value REAL,
            Recipe TEXT,
            FOREIGN KEY(Lot_ID) REFERENCES Lots(Lot_ID)
        )
    ''')
    
    # Table: Defects (For Pareto & Yield Analysis)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Defects (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Lot_ID TEXT,
            Wafer_ID TEXT,
            Defect_Type TEXT,
            Count INTEGER,
            Severity TEXT,
            Timestamp TIMESTAMP,
            FOREIGN KEY(Lot_ID) REFERENCES Lots(Lot_ID)
        )
    ''')
    
    # Table: DOE_Experiments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DOE_Experiments (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Experiment_Name TEXT,
            Factor_1 TEXT,
            Factor_2 TEXT,
            Response_Variable TEXT,
            Data_JSON TEXT,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table: GRR_Studies (MSA/GR&R study metadata)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GRR_Studies (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Study_Name TEXT NOT NULL,
            Description TEXT,
            Method TEXT DEFAULT 'ANOVA',
            Gauge_Name TEXT,
            Gauge_Type TEXT,
            USL REAL,
            LSL REAL,
            Tolerance REAL,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table: GRR_Measurements (individual measurements for GR&R)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GRR_Measurements (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Study_ID INTEGER,
            Part_ID TEXT NOT NULL,
            Operator_ID TEXT NOT NULL,
            Trial INTEGER NOT NULL,
            Value REAL NOT NULL,
            FOREIGN KEY(Study_ID) REFERENCES GRR_Studies(ID)
        )
    ''')

    conn.commit()
    conn.close()

def get_connection():
    """Get a database connection."""
    if not os.path.exists(DB_PATH):
        init_db()
    return sqlite3.connect(DB_PATH)

def run_query(query, params=None):
    """Execute a query and return results as DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
    return df

def insert_query(query, params):
    """Execute an insert/update query."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()
