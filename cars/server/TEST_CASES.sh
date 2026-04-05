# 🏎️ Shelby American API – Test Playbook
# =====================================================================
# Run the server first:
#   cd cars/server
#   uv run uvicorn src.main:app --reload
#
# Then hit it with these curl commands (or paste into Postman / HTTPie).
# BASE_URL defaults to http://localhost:8000
# =====================================================================

BASE_URL="http://localhost:8000"

# ─────────────────────────────────────────────────────────────────────
# 1. META ENDPOINTS
# ─────────────────────────────────────────────────────────────────────

# 1a. Root welcome message
curl -s "$BASE_URL/" | python3 -m json.tool

# 1b. Health check (expect status: "ok", 2 components)
curl -s "$BASE_URL/health" | python3 -m json.tool

# 1c. OpenAPI interactive docs (open in browser)
#  → http://localhost:8000/docs
#  → http://localhost:8000/redoc


# ─────────────────────────────────────────────────────────────────────
# 2. HAPPY PATH – GET
# ─────────────────────────────────────────────────────────────────────

# 2a. List all cars (expect 5 cars from seed data)
curl -s "$BASE_URL/api/v1/cars" | python3 -m json.tool

# 2b. Get a single car (ID = 1)
curl -s "$BASE_URL/api/v1/cars/1" | python3 -m json.tool

# 2c. Filter by brand (Ferrari – expect 2 results)
curl -s "$BASE_URL/api/v1/cars?brand=Ferrari" | python3 -m json.tool

# 2d. Filter by brand – case-insensitive (ferrARI should work too)
curl -s "$BASE_URL/api/v1/cars?brand=ferrARI" | python3 -m json.tool

# 2e. Price range filter (expect cars between ₹1 Cr and ₹4 Cr)
curl -s "$BASE_URL/api/v1/cars?min_price=1.0&max_price=4.0" | python3 -m json.tool

# 2f. Pagination – first page of 2
curl -s "$BASE_URL/api/v1/cars?limit=2&offset=0" | python3 -m json.tool

# 2g. Pagination – second page of 2
curl -s "$BASE_URL/api/v1/cars?limit=2&offset=2" | python3 -m json.tool

# 2h. Offset beyond data length (expect empty list [])
curl -s "$BASE_URL/api/v1/cars?offset=9999" | python3 -m json.tool

# 2i. Combined filter: brand + max_price
curl -s "$BASE_URL/api/v1/cars?brand=Ferrari&max_price=8.0" | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 3. HAPPY PATH – POST (create)
# ─────────────────────────────────────────────────────────────────────

# 3a. Create a valid new car (expect 201 Created)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aventador SVJ",
    "brand": "Lamborghini",
    "price": "₹8.00 Cr",
    "image_url": "https://example.com/aventador.jpg"
  }' | python3 -m json.tool

# 3b. Create without image_url (optional field – expect 201)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Continental GT",
    "brand": "Bentley",
    "price": "₹4.10 Cr"
  }' | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 4. HAPPY PATH – PUT (update)
# ─────────────────────────────────────────────────────────────────────

# 4a. Update just the price of car 3
curl -s -X PUT "$BASE_URL/api/v1/cars/3" \
  -H "Content-Type: application/json" \
  -d '{"price": "₹2.00 Cr"}' | python3 -m json.tool

# 4b. Update multiple fields at once
curl -s -X PUT "$BASE_URL/api/v1/cars/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": "₹11.00 Cr",
    "image_url": "https://example.com/new-ferrari.jpg"
  }' | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 5. HAPPY PATH – DELETE
# ─────────────────────────────────────────────────────────────────────

# 5a. Delete car with ID 5 (Huracán EVO)
curl -s -X DELETE "$BASE_URL/api/v1/cars/5" | python3 -m json.tool

# 5b. Confirm it's gone (expect 404 after delete)
curl -s "$BASE_URL/api/v1/cars/5" | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 6. ERROR CASES – 404 Not Found
# ─────────────────────────────────────────────────────────────────────

# 6a. Get non-existent car (expect error_code: CAR_NOT_FOUND, 404)
curl -s "$BASE_URL/api/v1/cars/999" | python3 -m json.tool

# 6b. Update non-existent car (expect 404)
curl -s -X PUT "$BASE_URL/api/v1/cars/999" \
  -H "Content-Type: application/json" \
  -d '{"price": "₹1.00 Cr"}' | python3 -m json.tool

# 6c. Delete non-existent car (expect 404)
curl -s -X DELETE "$BASE_URL/api/v1/cars/999" | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 7. ERROR CASES – 409 Conflict (Duplicate)
# ─────────────────────────────────────────────────────────────────────

# 7a. Create a duplicate car (same name+brand as seed data – expect 409)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SF90 XX Stradale",
    "brand": "Ferrari",
    "price": "₹6.90 Cr"
  }' | python3 -m json.tool

# 7b. Update car 3 to collide with car 1 (name+brand already exists)
curl -s -X PUT "$BASE_URL/api/v1/cars/3" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "849 Testarossa",
    "brand": "Ferrari"
  }' | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 8. ERROR CASES – 422 Pydantic Validation
# ─────────────────────────────────────────────────────────────────────

# 8a. Missing required field `brand`
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Car",
    "price": "₹1.00 Cr"
  }' | python3 -m json.tool

# 8b. Wrong price format (no ₹ symbol)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Car",
    "brand": "Test Brand",
    "price": "10.37 Crore"
  }' | python3 -m json.tool

# 8c. Price with wrong suffix
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Car",
    "brand": "Test Brand",
    "price": "₹10.37"
  }' | python3 -m json.tool

# 8d. Name too short (less than 2 chars)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "X",
    "brand": "Ferrari",
    "price": "₹1.00 Cr"
  }' | python3 -m json.tool

# 8e. Invalid image_url (not http/https)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Valid Car",
    "brand": "Valid Brand",
    "price": "₹1.00 Cr",
    "image_url": "ftp://invalid.com/image.jpg"
  }' | python3 -m json.tool

# 8f. Completely empty body (expect 422)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool

# 8g. Non-JSON body (expect 422)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d 'not valid json at all' | python3 -m json.tool

# 8h. limit out of range (>100 – expect 422)
curl -s "$BASE_URL/api/v1/cars?limit=9999" | python3 -m json.tool

# 8i. negative offset (expect 422)
curl -s "$BASE_URL/api/v1/cars?offset=-5" | python3 -m json.tool

# 8j. min_price is negative (expect 422)
curl -s "$BASE_URL/api/v1/cars?min_price=-1" | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 9. ERROR CASES – 400 Bad Request (Business Validation)
# ─────────────────────────────────────────────────────────────────────

# 9a. PUT with all-null payload (Pydantic model_validator catches this – 422)
curl -s -X PUT "$BASE_URL/api/v1/cars/1" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool

# 9b. PUT with explicit nulls (same – model_validator triggers)
curl -s -X PUT "$BASE_URL/api/v1/cars/1" \
  -H "Content-Type: application/json" \
  -d '{"name": null, "brand": null, "price": null, "image_url": null}' \
  | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 10. EDGE CASES – Path Parameter Types
# ─────────────────────────────────────────────────────────────────────

# 10a. String instead of int in path (FastAPI catches this – 422)
curl -s "$BASE_URL/api/v1/cars/abc" | python3 -m json.tool

# 10b. Float instead of int in path (422)
curl -s "$BASE_URL/api/v1/cars/1.5" | python3 -m json.tool

# 10c. car_id = 0 (our service raises InvalidIDException – expect 400)
curl -s "$BASE_URL/api/v1/cars/0" | python3 -m json.tool

# 10d. Negative car_id (expect 400)
curl -s "$BASE_URL/api/v1/cars/-1" | python3 -m json.tool

# 10e. Very large ID (expect 404 – not found, not crash)
curl -s "$BASE_URL/api/v1/cars/2147483647" | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 11. EDGE CASES – Data Oddities
# ─────────────────────────────────────────────────────────────────────

# 11a. Filter by brand that doesn't exist (expect empty list, not 404)
curl -s "$BASE_URL/api/v1/cars?brand=Bugatti" | python3 -m json.tool

# 11b. min_price higher than max_price (logical contradiction – empty list)
curl -s "$BASE_URL/api/v1/cars?min_price=10.0&max_price=1.0" | python3 -m json.tool

# 11c. Price exactly on boundary (should be included)
curl -s "$BASE_URL/api/v1/cars?min_price=1.81&max_price=1.81" | python3 -m json.tool

# 11d. Extra unknown fields in POST body (Pydantic ignores by default)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Phantom VIII",
    "brand": "Rolls-Royce",
    "price": "₹9.50 Cr",
    "unknown_field": "this should be silently ignored",
    "another_bad_key": 42
  }' | python3 -m json.tool

# 11e. Leading/trailing whitespace in name/brand (validators strip it)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "  Ghost  ",
    "brand": "  Rolls-Royce  ",
    "price": "₹7.95 Cr"
  }' | python3 -m json.tool

# 11f. Unicode characters in name/brand (should work fine)
curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GLC 300 4MATIC® Coupé",
    "brand": "Mercedes‑Benz",
    "price": "₹1.20 Cr"
  }' | python3 -m json.tool


# ─────────────────────────────────────────────────────────────────────
# 12. WORKFLOW – Full CRUD cycle
# ─────────────────────────────────────────────────────────────────────

# Step 1: Create
NEW_ID=$(curl -s -X POST "$BASE_URL/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "720S Spider",
    "brand": "McLaren",
    "price": "₹4.70 Cr",
    "image_url": "https://example.com/720s.jpg"
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['id'])")

echo "Created car ID: $NEW_ID"

# Step 2: Read it back
curl -s "$BASE_URL/api/v1/cars/$NEW_ID" | python3 -m json.tool

# Step 3: Update it
curl -s -X PUT "$BASE_URL/api/v1/cars/$NEW_ID" \
  -H "Content-Type: application/json" \
  -d '{"price": "₹5.00 Cr"}' | python3 -m json.tool

# Step 4: Confirm update
curl -s "$BASE_URL/api/v1/cars/$NEW_ID" | python3 -m json.tool

# Step 5: Delete it
curl -s -X DELETE "$BASE_URL/api/v1/cars/$NEW_ID" | python3 -m json.tool

# Step 6: Confirm 404 after delete
curl -s "$BASE_URL/api/v1/cars/$NEW_ID" | python3 -m json.tool