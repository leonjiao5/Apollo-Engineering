import sqlite3

cx = sqlite3.connect('vehicles.db')
cu = cx.cursor()

create_table = """
CREATE TABLE IF NOT EXISTS Vehicle (
    vin TEXT PRIMARY KEY NOT NULL UNIQUE,
    manufacturer_name TEXT NOT NULL,
    description TEXT,
    horse_power INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    model_year INTEGER NOT NULL,
    purchase_price REAL NOT NULL,
    fuel_type TEXT NOT NULL
);
"""

cu.execute(create_table)

cx.commit()
cx.close()