from flask import Flask, request, jsonify
import sqlite3
import uuid

app = Flask(__name__)
DATABASE = "vehicles.db"

"""
Opens a connection to the database.
"""
def get_db_connection():
    cx = sqlite3.connect(DATABASE)
    cx.row_factory = sqlite3.Row  # Enable dictionary-like row access
    return cx

"""
Check if the fields in data match the expected format. Returns a list of errors, if any.
"""
def check_fields(data):
    fields = {
        "manufacturer_name": str,
        "horse_power": int,
        "model_name": str,
        "model_year": int,
        "purchase_price": float,
        "fuel_type": str,
    }

    # check for missing or invalid fields
    errors = []
    for field, field_type in fields.items(): 
        if field not in data:
            errors.append(f"'{field}' is required.")
        elif not isinstance(data[field], field_type):
            errors.append(f"'{field}' must be of type {field_type.__name__}.")

    if "description" in data and not isinstance(data["description"], str):
        errors.append("'description' must be a string.")

    return errors


"""
Return a JSON representation of all records in the Vehicle table
"""
@app.route("/vehicle", methods=["GET"])
def get_all_vehicles():
    cx = get_db_connection()
    vehicles = cx.execute("SELECT * FROM Vehicle").fetchall()
    cx.close()
    return jsonify([dict(vehicle) for vehicle in vehicles]), 200

"""
Return a JSON representation of a new vehicle. Raises '400 Bad Request' error if 
request entity cannot be parsed in JSON format. Raises '422 Unprocessable Entity' 
if request entity is invalid.
"""
@app.route("/vehicle", methods=["POST"])
def create_vehicle():
    try: 
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Bad Request"}), 400

    errors = check_fields(data)
    if errors:
        return jsonify({"errors": errors}), 422

    vin = str(uuid.uuid4())
    try:
        cx = get_db_connection()
        cx.execute(
            """
            INSERT INTO Vehicle (vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                vin,
                data["manufacturer_name"],
                data.get("description", None),
                data["horse_power"],
                data["model_name"],
                data["model_year"],
                data["purchase_price"],
                data["fuel_type"],
            ),
        )
        cx.commit()
        cx.close()
        return jsonify({"message": "Vehicle created successfully", "vehicle": data}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Unprocessable Entity"}), 422

"""
Return a JSON representation of a vehicle by its vehicle ID. Raises '404 Value Error'
if vehicle ID does not exist.
"""
@app.route("/vehicle/<vin>", methods=["GET"])
def get_vehicle(vin):
    cx = get_db_connection()
    vehicle = cx.execute("SELECT * FROM Vehicle WHERE vin = ?", (vin,)).fetchone()
    cx.close()
    if vehicle:
        return jsonify(dict(vehicle)), 200
    else:
        return jsonify({"error": "Vehicle not found"}), 404

"""
Return a JSON representation of the updated vehicle given its vehicle ID. Raises
'400 Bad Request' error if request entity cannot be parsed in JSON format. Raises 
'404 Value Error' if vehicle ID does not exist.
"""
@app.route("/vehicle/<vin>", methods=["PUT"])
def update_vehicle(vin):
    try: 
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Bad Request"}), 400

    cx = get_db_connection()
    vehicle = cx.execute("SELECT * FROM Vehicle WHERE vin = ?", (vin,)).fetchone()
    if not vehicle:
        cx.close()
        return jsonify({"error": "Vehicle not found"}), 404

    errors = check_fields(data)
    if errors:
        return jsonify({"errors": errors}), 422

    try:
        cx.execute(
            """
            UPDATE Vehicle
            SET manufacturer_name = ?, description = ?, horse_power = ?, model_name = ?, model_year = ?, purchase_price = ?, fuel_type = ?
            WHERE vin = ?
            """,
            (
                data["manufacturer_name"],
                data.get("description", None),
                data["horse_power"],
                data["model_name"],
                data["model_year"],
                data["purchase_price"],
                data["fuel_type"],
                vin,
            ),
        )
        cx.commit()
        cx.close()
        return jsonify({"message": "Vehicle updated successfully"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Unprocessable Entity"}), 422

"""
Deletes the vehicle with vehicle ID 'vin' from the Vehicle table.
"""
@app.route("/vehicle/<vin>", methods=["DELETE"])
def delete_vehicle(vin):
    cx = get_db_connection()
    cx.execute("DELETE FROM Vehicle WHERE vin = ?", (vin,))
    cx.commit()
    cx.close()
    return jsonify({"message": "Vehicle deleted successfully"}), 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)

