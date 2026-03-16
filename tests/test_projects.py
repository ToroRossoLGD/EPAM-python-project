import pytest


async def register_and_login(client, login: str, password: str = "password123") -> str:
    register_response = await client.post(
        "/auth",
        json={
            "login": login,
            "password": password,
            "repeat_password": password,
        },
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/login",
        json={
            "login": login,
            "password": password,
        },
    )
    assert login_response.status_code == 200

    return login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_and_list_projects(client):
    token = await register_and_login(client, "projectuser")

    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/projects",
        json={
            "name": "My Test Project",
            "description": "Project description",
        },
        headers=headers,
    )

    assert create_response.status_code == 201
    created_project = create_response.json()

    assert created_project["name"] == "My Test Project"
    assert created_project["description"] == "Project description"
    assert "id" in created_project
    assert "owner_id" in created_project

    list_response = await client.get("/projects", headers=headers)
    assert list_response.status_code == 200

    projects = list_response.json()
    assert len(projects) == 1
    assert projects[0]["name"] == "My Test Project"


@pytest.mark.asyncio
async def test_get_and_update_project_info(client):
    token = await register_and_login(client, "infouser")

    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/projects",
        json={
            "name": "Initial Project",
            "description": "Initial description",
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    get_response = await client.get(f"/project/{project_id}/info", headers=headers)
    assert get_response.status_code == 200

    project_data = get_response.json()
    assert project_data["name"] == "Initial Project"
    assert project_data["description"] == "Initial description"

    update_response = await client.put(
        f"/project/{project_id}/info",
        json={
            "name": "Updated Project",
            "description": "Updated description",
        },
        headers=headers,
    )
    assert update_response.status_code == 200

    updated_data = update_response.json()
    assert updated_data["name"] == "Updated Project"
    assert updated_data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_project(client):
    token = await register_and_login(client, "deleteuser")

    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/projects",
        json={
            "name": "Project To Delete",
            "description": "Delete me",
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    delete_response = await client.delete(f"/project/{project_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = await client.get(f"/project/{project_id}/info", headers=headers)
    assert get_response.status_code in (403, 404)