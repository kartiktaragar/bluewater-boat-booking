from datetime import date, timedelta


def test_create_booking_and_prevent_overlapping_booking(client, registered_user):
    token, _ = registered_user
    headers = {"Authorization": f"Bearer {token}"}
    start = date.today() + timedelta(days=10)
    request = {
        "boat_id": 1,
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=2)).isoformat(),
        "guests": 4,
    }

    created = client.post("/api/bookings", json=request, headers=headers)
    assert created.status_code == 201
    assert created.json()["total_price"] == "250.00"
    assert created.json()["payment"]["status"] == "pending"
    assert client.post("/api/bookings", json=request, headers=headers).status_code == 409


def test_adjacent_dates_do_not_overlap(client, registered_user):
    token, _ = registered_user
    headers = {"Authorization": f"Bearer {token}"}
    start = date.today() + timedelta(days=20)
    first = {
        "boat_id": 1,
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=2)).isoformat(),
        "guests": 2,
    }
    second = {
        **first,
        "start_date": (start + timedelta(days=2)).isoformat(),
        "end_date": (start + timedelta(days=4)).isoformat(),
    }
    assert client.post("/api/bookings", json=first, headers=headers).status_code == 201
    assert client.post("/api/bookings", json=second, headers=headers).status_code == 201


def test_booking_validates_capacity_and_requires_auth(client, registered_user):
    token, _ = registered_user
    start = date.today() + timedelta(days=5)
    payload = {
        "boat_id": 1,
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=1)).isoformat(),
        "guests": 7,
    }
    assert client.post("/api/bookings", json=payload, headers={"Authorization": f"Bearer {token}"}).status_code == 422
    assert client.post("/api/bookings", json=payload).status_code == 401


def test_list_and_cancel_own_booking(client, registered_user):
    token, _ = registered_user
    headers = {"Authorization": f"Bearer {token}"}
    start = date.today() + timedelta(days=30)
    response = client.post(
        "/api/bookings",
        json={
            "boat_id": 1,
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=1)).isoformat(),
            "guests": 2,
        },
        headers=headers,
    )
    booking_id = response.json()["id"]
    assert client.get("/api/bookings/mine", headers=headers).json()[0]["id"] == booking_id
    assert client.post(f"/api/bookings/{booking_id}/cancel", headers=headers).json()["status"] == "cancelled"


def test_admin_cannot_reconfirm_overlapping_booking(client, registered_user, admin_token):
    customer_headers = {"Authorization": f"Bearer {registered_user[0]}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    start = date.today() + timedelta(days=40)
    payload = {
        "boat_id": 1,
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=2)).isoformat(),
        "guests": 2,
    }
    first = client.post("/api/bookings", json=payload, headers=customer_headers).json()
    client.post(f"/api/bookings/{first['id']}/cancel", headers=customer_headers)
    client.post("/api/bookings", json=payload, headers=customer_headers)

    response = client.patch(
        f"/api/admin/bookings/{first['id']}/status?booking_status=confirmed",
        headers=admin_headers,
    )
    assert response.status_code == 409
