# Electricity Price API

REST API for calculating mean electricity prices by Australian state.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
make install
```

## Run

```bash
make run
```

Server starts at `http://localhost:5000`

## Usage

Get mean price for a state:

```bash
curl "http://localhost:5000/api/v1/prices/mean?state=NSW"
```

Response:

```json
{ "state": "NSW", "mean_price": 62.29, "record_count": 336 }
```

List available states:

```bash
curl "http://localhost:5000/api/v1/states"
```

## Development

```bash
make test    # Run tests with coverage
make lint    # Check code style
make format  # Auto-format code
make help    # Show all commands
```
