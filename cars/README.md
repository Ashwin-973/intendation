Requiem for a Dream?

# 🏎️ Shelby American Car API

A **learning project** demonstrating professional-grade FastAPI patterns:
exception handling, structured logging, clean architecture, and full test coverage.

---

## Quick Start

```bash
cd cars/server

# Install dependencies
uv sync

# Run the server (hot-reload enabled)
uv run uvicorn src.main:app --reload

# Interactive docs
open http://localhost:8000/docs
```

---

## Project Structure

```
cars/server/
├── data.py                    # In-memory mock database (list[dict])
├── pyproject.toml             # uv project config
├── pytest.ini                 # Test runner config
├── TEST_CASES.sh              # curl playbook for manual testing
│
├── tests/
│   └── test_cars.py           # 60+ pytest test cases
│
└── src/
    ├── config.py              # Centralised settings (env-driven)
    ├── exceptions.py          # Custom exception hierarchy
    ├── logger.py              # Structured coloured logging
    ├── middleware.py          # Global exception → JSON error handler
    ├── main.py                # App factory, lifespan, health check
    │
    ├── api/
    │   ├── dependencies.py    # Dependency injection wiring
    │   └── v1/
    │       └── cars.py        # Thin CRUD router
    │
    ├── db/
    │   └── session.py         # get_db() generator (drop-in for SQLAlchemy)
    │
    ├── schemas/
    │   └── car.py             # Pydantic v2 request/response + error schemas
    │
    └── services/
        └── cars.py            # All business logic (list, get, create, update, delete)
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/health` | App + component health |
| `GET` | `/api/v1/cars` | List cars (filter + paginate) |
| `GET` | `/api/v1/cars/{id}` | Get single car |
| `POST` | `/api/v1/cars` | Create new car |
| `PUT` | `/api/v1/cars/{id}` | Update existing car |
| `DELETE` | `/api/v1/cars/{id}` | Delete car |

### Query Parameters for `GET /api/v1/cars`

| Param | Type | Description |
|-------|------|-------------|
| `brand` | `string` | Case-insensitive brand filter |
| `min_price` | `float` | Minimum price in Crores |
| `max_price` | `float` | Maximum price in Crores |
| `limit` | `int` | Results per page (1–100, default 20) |
| `offset` | `int` | Records to skip (default 0) |

---

## Error Handling

Every non-2xx response returns a uniform envelope:

```json
{
  "error": true,
  "error_code": "CAR_NOT_FOUND",
  "message": "Car with ID 999 does not exist.",
  "detail": null,
  "path": "/api/v1/cars/999",
  "status_code": 404
}
```

### Exception Hierarchy

```
ShelbyBaseException
├── ValidationException         400  VALIDATION_ERROR
│   ├── InvalidPriceFormatException   INVALID_PRICE_FORMAT
│   ├── InvalidIDException            INVALID_ID
│   └── EmptyPayloadException         EMPTY_PAYLOAD
├── AuthenticationException     401  UNAUTHENTICATED
├── AuthorizationException      403  FORBIDDEN
├── NotFoundException           404  NOT_FOUND
│   └── CarNotFoundException          CAR_NOT_FOUND
├── RequestTimeoutException     408  REQUEST_TIMEOUT
├── ConflictException           409  CONFLICT
│   └── DuplicateCarException         DUPLICATE_CAR
├── UnprocessableException      422  UNPROCESSABLE_ENTITY
├── RateLimitException          429  RATE_LIMIT_EXCEEDED
└── InternalServerException     500  INTERNAL_ERROR
    ├── DatabaseException             DATABASE_ERROR
    └── ServiceUnavailableException   SERVICE_UNAVAILABLE
```

---

## Price Format

All prices must follow the pattern: **`₹X.XX Cr`**

Valid: `₹10.37 Cr`, `₹1.81 Cr`, `₹999 Cr`  
Invalid: `10.37 Crore`, `₹10.37`, `Rs 10 Cr`

---

## Running Tests

```bash
cd cars/server
uv run pytest tests/ -v

# With coverage (install pytest-cov separately)
uv run pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Manual Testing

```bash
chmod +x TEST_CASES.sh
# Run individual sections or the full script
bash TEST_CASES.sh
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | `DEBUG / INFO / WARNING / ERROR` |
| `DEBUG` | `false` | Enables debug mode |
| `PORT` | `8000` | Server port |
| `HOST` | `0.0.0.0` | Server bind address |
| `DEFAULT_PAGE_SIZE` | `20` | Default pagination limit |
| `MAX_PAGE_SIZE` | `100` | Hard cap on pagination limit |

```bash
LOG_LEVEL=DEBUG uv run uvicorn src.main:app --reload
```

---

## Key Patterns Demonstrated

**1. Layered Architecture** — Router → Service → DB. Each layer has one job.

**2. Typed Exceptions** — No `raise HTTPException(status_code=404)` scattered in routes. Raise `CarNotFoundException`, let middleware handle HTTP mapping.

**3. Uniform Error Envelope** — Every error, whether from Pydantic, your code, or an unexpected crash, returns the same JSON shape.

**4. Structured Logging** — Every log line carries context (`car_id`, `request_id`, `error_code`). No raw `print()`.

**5. Dependency Injection** — `get_db()` follows the same contract as a real SQLAlchemy session. Swap the implementation, not the interface.

**6. Pydantic v2 Validators** — Field-level `@field_validator` + cross-field `@model_validator` for business rules.