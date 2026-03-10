import pytest


async def register_login_and_create_project(client, login: str, password: str = "password123"):
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

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_response = await client.post(
        "/projects",
        json={
            "name": "Documents Project",
            "description": "Project for document tests",
        },
        headers=headers,
    )
    assert project_response.status_code == 201

    project_id = project_response.json()["id"]
    return headers, project_id

@pytest.mark.asyncio
async def test_document_upload_list_download_delete(client):
    headers, project_id = await register_login_and_create_project(client, "docuser")

    files = {
        "file": ("test.pdf", b"%PDF-1.4 fake pdf content", "application/pdf"),
    }

    upload_response = await client.post(
        f"/project/{project_id}/documents",
        files=files,
        headers=headers,
    )
    assert upload_response.status_code == 201

    document = upload_response.json()
    assert document["filename"] == "test.pdf"
    assert document["project_id"] == project_id
    assert "id" in document

    document_id = document["id"]

    list_response = await client.get(
        f"/project/{project_id}/documents",
        headers=headers,
    )
    assert list_response.status_code == 200

    documents = list_response.json()
    assert len(documents) == 1
    assert documents[0]["filename"] == "test.pdf"

    download_response = await client.get(
        f"/document/{document_id}",
        headers=headers,
    )
    assert download_response.status_code == 200

    delete_response = await client.delete(
        f"/document/{document_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    list_after_delete = await client.get(
        f"/project/{project_id}/documents",
        headers=headers,
    )
    assert list_after_delete.status_code == 200
    assert list_after_delete.json() == []

    @pytest.mark.asyncio
    async def test_document_reject_invalid_extension(client):
        headers, project_id = await register_login_and_create_project(client, "badfileuser")

        files = {
        "file": ("archive.rar", b"fake-rar-content", "application/x-rar-compressed"),
        }

        response = await client.post(
        f"/project/{project_id}/documents",
        files=files,
        headers=headers,
        )

        assert response.status_code == 400
        assert "Unsupported file extension" in response.json()["detail"]