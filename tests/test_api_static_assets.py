def test_static_assets_are_served_without_exposing_source_files(api_client):
    assert api_client.get("/").status_code == 200
    assert api_client.get("/style.css").status_code == 200
    assert api_client.get("/frontend/pages/cataloguePage.js").status_code == 200
    assert api_client.get("/admin.html").status_code == 200

    assert api_client.get("/app.py").status_code == 404
    assert api_client.get("/pyproject.toml").status_code == 404
