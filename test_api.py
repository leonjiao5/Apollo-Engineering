import unittest
import json
from api import app

"""Test Suite"""
class TestVehicleAPI(unittest.TestCase):

    """Set up the test client and clear the database"""
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # Clear the database before each test
        with app.app_context():
            from api import get_db_connection
            cx = get_db_connection()
            cx.execute("DELETE FROM Vehicle")
            cx.commit()
            cx.close()


    """Test creating a valid vehicle"""
    def test_post_valid_vehicle(self):
        response = self.client.post(
            "/vehicle",
            data=json.dumps({
                "manufacturer_name": "Toyota",
                "description": "Reliable car",
                "horse_power": 150,
                "model_name": "Corolla",
                "model_year": 2021,
                "purchase_price": 20000.99,
                "fuel_type": "Gasoline"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("vehicle", data)
        self.assertEqual(data["vehicle"]["manufacturer_name"], "Toyota")


    """Test creating a vehicle with malformed JSON"""
    def test_post_invalid_json(self):
        response = self.client.post(
            "/vehicle",
            data="{ manufacturer_name: Toyota }",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Bad Request")


    """Test creating a vehicle with missing fields"""
    def test_post_missing_field(self):
        response = self.client.post(
            "/vehicle",
            data=json.dumps({
                "manufacturer_name": "Toyota",
                "horse_power": 150,
                "model_year": 2021,
                "purchase_price": 20000.99,
                "fuel_type": "Gasoline"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn("errors", data)
        self.assertIn("'model_name' is required.", data["errors"])


    """Test retrieving all vehicles"""
    def test_get_all_vehicles(self):
        self.test_post_valid_vehicle()
        response = self.client.get("/vehicle")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)


    """Test retrieving a vehicle by VIN"""
    def test_get_vehicle_by_vin(self):
        response = self.client.post(
            "/vehicle",
            data=json.dumps({
                "manufacturer_name": "Honda",
                "description": "Compact SUV",
                "horse_power": 180,
                "model_name": "CR-V",
                "model_year": 2023,
                "purchase_price": 28000.00,
                "fuel_type": "Gasoline"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        vehicle = self.client.get("/vehicle").get_json()[0]
        vin = vehicle["vin"]

        response = self.client.get(f"/vehicle/{vin}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["manufacturer_name"], "Honda")
    

    """Test deleting a vehicle"""
    def test_delete_vehicle(self):
        self.test_post_valid_vehicle()
        response = self.client.get("/vehicle")
        vehicle = response.get_json()[0]
        vin = vehicle["vin"]

        response = self.client.delete(f"/vehicle/{vin}")
        self.assertEqual(response.status_code, 204)

        response = self.client.get(f"/vehicle/{vin}")
        self.assertEqual(response.status_code, 404)


    """Test updating a vehicle"""
    def test_update_vehicle(self):
        response = self.client.post(
            "/vehicle",
            data=json.dumps({
                "manufacturer_name": "Honda",
                "description": "Compact SUV",
                "horse_power": 180,
                "model_name": "CR-V",
                "model_year": 2023,
                "purchase_price": 28000.00,
                "fuel_type": "Gasoline"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        vehicle = self.client.get("/vehicle").get_json()[0]
        vin = vehicle["vin"]

        response = self.client.put(
            f"/vehicle/{vin}",
            data=json.dumps({
                "manufacturer_name": "Honda",
                "description": "Updated description",
                "horse_power": 200,
                "model_name": "CR-V",
                "model_year": 2024,
                "purchase_price": 29000.00,
                "fuel_type": "Gasoline"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/vehicle/{vin}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["description"], "Updated description")


if __name__ == "__main__":
    unittest.main()