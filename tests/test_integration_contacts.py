from fastapi import status

test_contact = {
    "name": "Johnny",
    "surname": "Doe",
    "email": "johnny@example.com",
    "phone": "+380931234567",
    "birthday": "1990-05-15",
}

contacts = [
    {
        "id": 1,
        "name": "Johnny",
        "surname": "Doe",
        "email": "johnny@example.com",
        "phone": "+380931234567",
        "birthday": "1990-05-15",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "info": "Test contact.",
    },
    {
        "id": 2,
        "name": "Kate",
        "surname": "Doe",
        "email": "kate@example.com",
        "phone": "+380675714569",
        "birthday": "1990-05-25",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "info": None,
    },
]

def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json=test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["name"] == test_contact["name"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["name"] == test_contact["name"]
    assert "id" in data

def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_get_contacts(client, get_token):
    response = client.get("/api/contacts", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == contacts[0]["name"]
    assert "id" in data[0]

def test_update_contact(client, get_token):
    response = client.put(
        "/api/contacts/1",
        json={
            "name": "new_test_contact",
            "surname": "Doe",
            "email": "new_test@example.com",
            "phone": "+380931234567",
            "birthday": "1990-05-15"
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["name"] == "new_test_contact"
    assert "id" in data

def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/api/contact/2",
        json={"name": "new_test_contact"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == "Not Found"

def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["name"] == "new_test_contact"
    assert "id" in data

def test_repeat_delete_tag(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"
#
