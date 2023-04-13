def test_list():
    # Create 2 test locations
    first = app_client.post(
        "/lists",
        json={
                "name": "Test List 1", 
                "description": "Test Description 1"
            },
        )
    assert first.status_code == 201
    assert first.headers["Location"].startswith("http://testserver/lists/")
    assert (
        app_client.post(
            "/lists",
            json={
                "name": "Test List 2",
                "description": "Test Description 2",
            },
        ).status_code
        ==201
    )

    # Get all lists
    response = app_client.get("/lists")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 2
    assert result[0]["name"] == "Test List 1"
    assert result[1]["name"] == "Test List 2"
    assert result[0]["createdDate"] is not None
    assert result[1]["createdDate"] is not None

    # Test those lists at the ID URL
    assert result[0]["id"] is not None
    test_list_id = result[0]["id"]
    test_list_id2 = result[1]["id"]

    response = app_client.get(f"/lists/{0}".format(test_list_id))
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "Test List 1"
    assert result["description"] == "Test Description 1"

    # Test a list with a bad ID