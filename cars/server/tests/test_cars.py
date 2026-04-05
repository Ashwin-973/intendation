"""
Test suite for Shelby American Car API.

Run with:
    cd cars/server
    uv run pytest tests/ -v

Requirements (already in pyproject.toml dev deps):
    httpx, pytest, pytest-asyncio
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# ── Path bootstrap ────────────────────────────────────────────────────────────
_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# ── We patch CAR_DB before importing the app so every test starts clean ───────
import data as _data_module  # noqa: E402

_SEED = [
    {
        "id": 1,
        "name": "849 Testarossa",
        "brand": "Ferrari",
        "price": "₹10.37 Cr",
        "image_url": "https://example.com/testarossa.jpg",
    },
    {
        "id": 2,
        "name": "SF90 XX Stradale",
        "brand": "Ferrari",
        "price": "₹6.90 Cr",
        "image_url": "https://example.com/sf90.jpg",
    },
    {
        "id": 3,
        "name": "S 350d",
        "brand": "Mercedes Benz",
        "price": "₹1.81 Cr",
        "image_url": "https://example.com/s350d.jpg",
    },
]


def _reset_db() -> None:
    """Restore CAR_DB to a clean copy of seed data before each test."""
    _data_module.CAR_DB.clear()
    _data_module.CAR_DB.extend([dict(car) for car in _SEED])


from src.main import app  # noqa: E402  (import after path + data setup)


@pytest.fixture(autouse=True)
def reset_db():
    """Auto-reset the in-memory DB before each test."""
    _reset_db()
    yield
    _reset_db()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


# ═════════════════════════════════════════════════════════════════════
# META ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

class TestMetaEndpoints:
    def test_root_returns_200(self, client: TestClient):
        r = client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert "message" in body
        assert "docs" in body
        assert "health" in body

    def test_health_check_ok(self, client: TestClient):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert "database" in body["components"]
        assert "model" in body["components"]
        assert body["components"]["database"]["status"] == "ok"

    def test_health_reports_car_count(self, client: TestClient):
        r = client.get("/health")
        body = r.json()
        # Seed has 3 cars
        assert "3 cars" in body["components"]["database"]["message"]


# ═════════════════════════════════════════════════════════════════════
# LIST CARS – GET /api/v1/cars
# ═════════════════════════════════════════════════════════════════════

class TestListCars:
    def test_returns_all_cars(self, client: TestClient):
        r = client.get("/api/v1/cars")
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_filter_by_brand_exact(self, client: TestClient):
        r = client.get("/api/v1/cars?brand=Ferrari")
        assert r.status_code == 200
        results = r.json()
        assert len(results) == 2
        assert all(c["brand"] == "Ferrari" for c in results)

    def test_filter_by_brand_case_insensitive(self, client: TestClient):
        r = client.get("/api/v1/cars?brand=fErRaRi")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_filter_by_brand_no_results(self, client: TestClient):
        r = client.get("/api/v1/cars?brand=Bugatti")
        assert r.status_code == 200
        assert r.json() == []

    def test_filter_by_min_price(self, client: TestClient):
        # Only Ferrari 849 Testarossa (₹10.37) above ₹8 Cr
        r = client.get("/api/v1/cars?min_price=8.0")
        assert r.status_code == 200
        results = r.json()
        assert len(results) == 1
        assert results[0]["name"] == "849 Testarossa"

    def test_filter_by_max_price(self, client: TestClient):
        # Only S 350d (₹1.81) below ₹3 Cr
        r = client.get("/api/v1/cars?max_price=3.0")
        assert r.status_code == 200
        results = r.json()
        assert len(results) == 1
        assert results[0]["brand"] == "Mercedes Benz"

    def test_filter_price_range(self, client: TestClient):
        # SF90 (₹6.90) is in 5–8 range
        r = client.get("/api/v1/cars?min_price=5.0&max_price=8.0")
        assert r.status_code == 200
        results = r.json()
        assert len(results) == 1
        assert results[0]["name"] == "SF90 XX Stradale"

    def test_price_on_boundary_included(self, client: TestClient):
        r = client.get("/api/v1/cars?min_price=1.81&max_price=1.81")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_impossible_price_range_empty(self, client: TestClient):
        r = client.get("/api/v1/cars?min_price=10.0&max_price=1.0")
        assert r.status_code == 200
        assert r.json() == []

    def test_pagination_limit(self, client: TestClient):
        r = client.get("/api/v1/cars?limit=2")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_pagination_offset(self, client: TestClient):
        r_all = client.get("/api/v1/cars").json()
        r_paged = client.get("/api/v1/cars?offset=1").json()
        assert r_paged == r_all[1:]

    def test_offset_beyond_data_returns_empty(self, client: TestClient):
        r = client.get("/api/v1/cars?offset=9999")
        assert r.status_code == 200
        assert r.json() == []

    def test_limit_too_high_is_422(self, client: TestClient):
        r = client.get("/api/v1/cars?limit=9999")
        assert r.status_code == 422
        assert r.json()["error_code"] == "VALIDATION_ERROR"

    def test_limit_zero_is_422(self, client: TestClient):
        r = client.get("/api/v1/cars?limit=0")
        assert r.status_code == 422

    def test_negative_offset_is_422(self, client: TestClient):
        r = client.get("/api/v1/cars?offset=-1")
        assert r.status_code == 422

    def test_negative_min_price_is_422(self, client: TestClient):
        r = client.get("/api/v1/cars?min_price=-1")
        assert r.status_code == 422

    def test_combined_brand_and_price_filter(self, client: TestClient):
        # Ferrari + max ₹7 → only SF90 (₹6.90)
        r = client.get("/api/v1/cars?brand=Ferrari&max_price=7.0")
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert r.json()[0]["name"] == "SF90 XX Stradale"


# ═════════════════════════════════════════════════════════════════════
# GET SINGLE CAR – GET /api/v1/cars/{id}
# ═════════════════════════════════════════════════════════════════════

class TestGetCar:
    def test_get_existing_car(self, client: TestClient):
        r = client.get("/api/v1/cars/1")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == 1
        assert body["name"] == "849 Testarossa"

    def test_all_seed_cars_retrievable(self, client: TestClient):
        for car_id in [1, 2, 3]:
            r = client.get(f"/api/v1/cars/{car_id}")
            assert r.status_code == 200, f"Car {car_id} not retrievable"

    def test_nonexistent_car_is_404(self, client: TestClient):
        r = client.get("/api/v1/cars/999")
        assert r.status_code == 404
        body = r.json()
        assert body["error"] is True
        assert body["error_code"] == "CAR_NOT_FOUND"
        assert body["path"] == "/api/v1/cars/999"

    def test_id_zero_is_400(self, client: TestClient):
        r = client.get("/api/v1/cars/0")
        assert r.status_code == 400
        assert r.json()["error_code"] == "INVALID_ID"

    def test_negative_id_is_400(self, client: TestClient):
        r = client.get("/api/v1/cars/-1")
        assert r.status_code == 400

    def test_string_id_is_422(self, client: TestClient):
        r = client.get("/api/v1/cars/abc")
        assert r.status_code == 422

    def test_float_id_is_422(self, client: TestClient):
        r = client.get("/api/v1/cars/1.5")
        assert r.status_code == 422

    def test_very_large_id_is_404_not_crash(self, client: TestClient):
        r = client.get("/api/v1/cars/2147483647")
        assert r.status_code == 404

    def test_response_has_all_fields(self, client: TestClient):
        r = client.get("/api/v1/cars/1")
        body = r.json()
        for field in ("id", "name", "brand", "price", "image_url"):
            assert field in body, f"Missing field: {field}"


# ═════════════════════════════════════════════════════════════════════
# CREATE CAR – POST /api/v1/cars
# ═════════════════════════════════════════════════════════════════════

class TestCreateCar:
    _valid = {
        "name": "Aventador SVJ",
        "brand": "Lamborghini",
        "price": "₹8.00 Cr",
        "image_url": "https://example.com/aventador.jpg",
    }

    def test_create_valid_car(self, client: TestClient):
        r = client.post("/api/v1/cars", json=self._valid)
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == "Aventador SVJ"
        assert "id" in body
        assert body["id"] == 4  # seeds have IDs 1-3

    def test_create_without_image_url(self, client: TestClient):
        payload = {k: v for k, v in self._valid.items() if k != "image_url"}
        r = client.post("/api/v1/cars", json=payload)
        assert r.status_code == 201
        assert r.json()["image_url"] is None

    def test_created_car_is_retrievable(self, client: TestClient):
        create_r = client.post("/api/v1/cars", json=self._valid)
        new_id = create_r.json()["id"]
        get_r = client.get(f"/api/v1/cars/{new_id}")
        assert get_r.status_code == 200
        assert get_r.json()["name"] == "Aventador SVJ"

    def test_duplicate_car_is_409(self, client: TestClient):
        # SF90 XX Stradale + Ferrari already exists in seed
        r = client.post("/api/v1/cars", json={
            "name": "SF90 XX Stradale",
            "brand": "Ferrari",
            "price": "₹6.90 Cr",
        })
        assert r.status_code == 409
        body = r.json()
        assert body["error_code"] == "DUPLICATE_CAR"

    def test_duplicate_check_case_insensitive(self, client: TestClient):
        r = client.post("/api/v1/cars", json={
            "name": "sf90 xx stradale",
            "brand": "ferrari",
            "price": "₹6.90 Cr",
        })
        assert r.status_code == 409

    def test_missing_required_field_brand(self, client: TestClient):
        r = client.post("/api/v1/cars", json={
            "name": "Test Car",
            "price": "₹1.00 Cr",
        })
        assert r.status_code == 422
        assert r.json()["error_code"] == "VALIDATION_ERROR"

    def test_missing_required_field_name(self, client: TestClient):
        r = client.post("/api/v1/cars", json={
            "brand": "Ferrari",
            "price": "₹1.00 Cr",
        })
        assert r.status_code == 422

    def test_missing_required_field_price(self, client: TestClient):
        r = client.post("/api/v1/cars", json={
            "name": "Test",
            "brand": "Ferrari",
        })
        assert r.status_code == 422

    def test_wrong_price_format_no_symbol(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "price": "10.37 Crore"})
        assert r.status_code == 422
        detail = r.json()["detail"]
        assert any("price" in str(e).lower() or "Price" in str(e) for e in detail)

    def test_wrong_price_format_no_cr_suffix(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "price": "₹10.37"})
        assert r.status_code == 422

    def test_wrong_price_format_plain_number(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "price": "10"})
        assert r.status_code == 422

    def test_price_too_many_decimal_places(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "price": "₹10.375 Cr"})
        assert r.status_code == 422

    def test_name_too_short(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "name": "X"})
        assert r.status_code == 422

    def test_brand_too_short(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "brand": "A"})
        assert r.status_code == 422

    def test_invalid_image_url_ftp(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "image_url": "ftp://img.com/x.jpg"})
        assert r.status_code == 422

    def test_invalid_image_url_no_scheme(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "image_url": "img.com/x.jpg"})
        assert r.status_code == 422

    def test_empty_body_is_422(self, client: TestClient):
        r = client.post("/api/v1/cars", json={})
        assert r.status_code == 422

    def test_extra_unknown_fields_ignored(self, client: TestClient):
        payload = {**self._valid, "surprise_key": "ignored", "num_wheels": 4}
        r = client.post("/api/v1/cars", json=payload)
        assert r.status_code == 201
        assert "surprise_key" not in r.json()

    def test_whitespace_stripped_from_name(self, client: TestClient):
        payload = {**self._valid, "name": "  Aventador SVJ  "}
        r = client.post("/api/v1/cars", json=payload)
        assert r.status_code == 201
        assert r.json()["name"] == "Aventador SVJ"

    def test_whitespace_stripped_from_brand(self, client: TestClient):
        payload = {**self._valid, "brand": "  Lamborghini  "}
        r = client.post("/api/v1/cars", json=payload)
        assert r.status_code == 201
        assert r.json()["brand"] == "Lamborghini"

    def test_ids_auto_increment(self, client: TestClient):
        r1 = client.post("/api/v1/cars", json=self._valid).json()
        r2 = client.post("/api/v1/cars", json={**self._valid, "brand": "McLaren"}).json()
        assert r2["id"] == r1["id"] + 1

    def test_price_without_decimal_accepted(self, client: TestClient):
        r = client.post("/api/v1/cars", json={**self._valid, "price": "₹10 Cr"})
        assert r.status_code == 201


# ═════════════════════════════════════════════════════════════════════
# UPDATE CAR – PUT /api/v1/cars/{id}
# ═════════════════════════════════════════════════════════════════════

class TestUpdateCar:
    def test_update_price_only(self, client: TestClient):
        r = client.put("/api/v1/cars/3", json={"price": "₹2.00 Cr"})
        assert r.status_code == 200
        assert r.json()["price"] == "₹2.00 Cr"
        # Other fields unchanged
        assert r.json()["name"] == "S 350d"

    def test_update_multiple_fields(self, client: TestClient):
        r = client.put("/api/v1/cars/1", json={
            "price": "₹11.00 Cr",
            "image_url": "https://example.com/new.jpg",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["price"] == "₹11.00 Cr"
        assert body["image_url"] == "https://example.com/new.jpg"

    def test_update_nonexistent_car_is_404(self, client: TestClient):
        r = client.put("/api/v1/cars/999", json={"price": "₹1.00 Cr"})
        assert r.status_code == 404
        assert r.json()["error_code"] == "CAR_NOT_FOUND"

    def test_update_empty_body_is_422(self, client: TestClient):
        r = client.put("/api/v1/cars/1", json={})
        assert r.status_code == 422

    def test_update_all_null_fields_is_422(self, client: TestClient):
        r = client.put("/api/v1/cars/1", json={
            "name": None, "brand": None, "price": None, "image_url": None
        })
        assert r.status_code == 422

    def test_update_creates_name_brand_conflict_is_409(self, client: TestClient):
        # Try to rename car 3 to match car 1 (same name + brand)
        r = client.put("/api/v1/cars/3", json={
            "name": "849 Testarossa",
            "brand": "Ferrari",
        })
        assert r.status_code == 409
        assert r.json()["error_code"] == "DUPLICATE_CAR"

    def test_update_same_car_no_conflict(self, client: TestClient):
        # Updating name+brand to the SAME values on the same car is fine
        r = client.put("/api/v1/cars/1", json={
            "name": "849 Testarossa",
            "brand": "Ferrari",
            "price": "₹10.37 Cr",
        })
        assert r.status_code == 200

    def test_update_zero_id_is_400(self, client: TestClient):
        r = client.put("/api/v1/cars/0", json={"price": "₹1.00 Cr"})
        assert r.status_code == 400

    def test_update_invalid_price_format(self, client: TestClient):
        r = client.put("/api/v1/cars/1", json={"price": "10 crore"})
        assert r.status_code == 422

    def test_update_persists_in_db(self, client: TestClient):
        client.put("/api/v1/cars/1", json={"price": "₹99.99 Cr"})
        r = client.get("/api/v1/cars/1")
        assert r.json()["price"] == "₹99.99 Cr"

    def test_update_image_url_to_null_clears_it(self, client: TestClient):
        # Explicitly sending null should keep it as null
        r = client.put("/api/v1/cars/1", json={"image_url": None, "price": "₹10.37 Cr"})
        # model_dump(exclude_none=True) will ignore null image_url and use price
        assert r.status_code == 200


# ═════════════════════════════════════════════════════════════════════
# DELETE CAR – DELETE /api/v1/cars/{id}
# ═════════════════════════════════════════════════════════════════════

class TestDeleteCar:
    def test_delete_existing_car(self, client: TestClient):
        r = client.delete("/api/v1/cars/1")
        assert r.status_code == 200
        assert r.json()["id"] == 1

    def test_delete_removes_from_db(self, client: TestClient):
        client.delete("/api/v1/cars/1")
        r = client.get("/api/v1/cars/1")
        assert r.status_code == 404

    def test_delete_reduces_list_count(self, client: TestClient):
        client.delete("/api/v1/cars/1")
        r = client.get("/api/v1/cars")
        assert len(r.json()) == 2

    def test_delete_nonexistent_is_404(self, client: TestClient):
        r = client.delete("/api/v1/cars/999")
        assert r.status_code == 404
        assert r.json()["error_code"] == "CAR_NOT_FOUND"

    def test_double_delete_second_is_404(self, client: TestClient):
        client.delete("/api/v1/cars/1")
        r = client.delete("/api/v1/cars/1")
        assert r.status_code == 404

    def test_delete_zero_id_is_400(self, client: TestClient):
        r = client.delete("/api/v1/cars/0")
        assert r.status_code == 400

    def test_delete_negative_id_is_400(self, client: TestClient):
        r = client.delete("/api/v1/cars/-5")
        assert r.status_code == 400


# ═════════════════════════════════════════════════════════════════════
# ERROR ENVELOPE STRUCTURE
# ═════════════════════════════════════════════════════════════════════

class TestErrorEnvelope:
    """
    Regardless of the error type, the JSON envelope must always
    contain the same fields.
    """

    _required_fields = {"error", "error_code", "message", "path", "status_code"}

    def _assert_envelope(self, body: dict, path: str, expected_status: int):
        for field in self._required_fields:
            assert field in body, f"Missing field '{field}' in error response"
        assert body["error"] is True
        assert body["status_code"] == expected_status
        assert body["path"] == path

    def test_404_envelope(self, client: TestClient):
        r = client.get("/api/v1/cars/999")
        self._assert_envelope(r.json(), "/api/v1/cars/999", 404)

    def test_409_envelope(self, client: TestClient):
        r = client.post("/api/v1/cars", json={
            "name": "SF90 XX Stradale",
            "brand": "Ferrari",
            "price": "₹6.90 Cr",
        })
        self._assert_envelope(r.json(), "/api/v1/cars", 409)

    def test_422_envelope(self, client: TestClient):
        r = client.get("/api/v1/cars/abc")
        self._assert_envelope(r.json(), "/api/v1/cars/abc", 422)

    def test_400_envelope(self, client: TestClient):
        r = client.get("/api/v1/cars/0")
        self._assert_envelope(r.json(), "/api/v1/cars/0", 400)


# ═════════════════════════════════════════════════════════════════════
# FULL CRUD LIFECYCLE
# ═════════════════════════════════════════════════════════════════════

class TestCRUDLifecycle:
    def test_create_read_update_delete(self, client: TestClient):
        # Create
        r = client.post("/api/v1/cars", json={
            "name": "720S Spider",
            "brand": "McLaren",
            "price": "₹4.70 Cr",
        })
        assert r.status_code == 201
        car_id = r.json()["id"]

        # Read
        r = client.get(f"/api/v1/cars/{car_id}")
        assert r.status_code == 200
        assert r.json()["name"] == "720S Spider"

        # Update
        r = client.put(f"/api/v1/cars/{car_id}", json={"price": "₹5.00 Cr"})
        assert r.status_code == 200
        assert r.json()["price"] == "₹5.00 Cr"

        # Confirm update persisted
        r = client.get(f"/api/v1/cars/{car_id}")
        assert r.json()["price"] == "₹5.00 Cr"

        # Delete
        r = client.delete(f"/api/v1/cars/{car_id}")
        assert r.status_code == 200

        # Confirm gone
        r = client.get(f"/api/v1/cars/{car_id}")
        assert r.status_code == 404

    def test_create_10_cars_sequential_ids(self, client: TestClient):
        base = {"brand": "Test", "price": "₹1.00 Cr"}
        ids = []
        for i in range(10):
            r = client.post("/api/v1/cars", json={**base, "name": f"Car Model {i}"})
            assert r.status_code == 201
            ids.append(r.json()["id"])
        # IDs must be strictly monotonically increasing
        assert ids == sorted(ids)
        assert len(set(ids)) == 10  # all unique