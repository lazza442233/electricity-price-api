class TestMeanPriceEndpoint:
    def test_valid_state(self, client):
        response = client.get("/api/v1/prices/mean?state=NSW")

        assert response.status_code == 200
        data = response.get_json()
        assert data["state"] == "NSW"
        assert "mean_price" in data
        assert "record_count" in data
        assert isinstance(data["mean_price"], float)

    def test_case_insensitive(self, client):
        responses = [
            client.get("/api/v1/prices/mean?state=nsw"),
            client.get("/api/v1/prices/mean?state=NSW"),
            client.get("/api/v1/prices/mean?state=Nsw"),
        ]

        prices = [r.get_json()["mean_price"] for r in responses]
        assert len(set(prices)) == 1

    def test_missing_state_parameter(self, client):
        response = client.get("/api/v1/prices/mean")

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "hint" in data

    def test_empty_state_parameter(self, client):
        response = client.get("/api/v1/prices/mean?state=")

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_whitespace_state_parameter(self, client):
        response = client.get("/api/v1/prices/mean?state=%20%20")

        assert response.status_code == 400

    def test_unknown_state(self, client):
        response = client.get("/api/v1/prices/mean?state=UNKNOWN")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert "Available states" in data["error"]

    def test_invalid_state_format_special_chars(self, client):
        response = client.get("/api/v1/prices/mean?state=NSW!")

        assert response.status_code == 400

    def test_invalid_state_format_numbers(self, client):
        response = client.get("/api/v1/prices/mean?state=123")

        assert response.status_code == 400

    def test_invalid_state_format_too_long(self, client):
        response = client.get("/api/v1/prices/mean?state=" + "A" * 100)

        assert response.status_code == 400


class TestStatesEndpoint:
    def test_list_states(self, client):
        response = client.get("/api/v1/states")

        assert response.status_code == 200
        data = response.get_json()
        assert "states" in data
        assert isinstance(data["states"], list)
        assert set(data["states"]) == {"NSW", "VIC"}


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "record_count" in data
        assert isinstance(data["record_count"], int)
