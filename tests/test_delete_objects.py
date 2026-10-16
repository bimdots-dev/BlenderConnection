import os
from http_client import send_request_with_headers
from payloads import unique_name, make_triangle_mesh, make_update_meshes_payload

def test_http_post_delete_objects (base_url):
    url = f"{base_url}/update-meshes"
    payload = {
        "model_name": "DeleteElementsTestModel",
        "materials": [
            {
                "name": "Red",
                "color": [1.0, 0.0, 0.0],
                "metallic": 0.0,
                "roughness": 0.5,
                "alpha": 0.8
            }
        ],
        "meshes": [
            {
                "id": "MyElementID",
                "name": "MyElementName",
                "checksum": "MyElementChecksum",
                "location": [0, 0, 0],
                "vertices": [
                    0.0, 0.0, 0.0,
                    1.0, 0.0, 0.0,
                    1.0, 1.0, 0.0
                ],
                "normals": [
                    0.0, 0.0, 1.0,
                    0.0, 0.0, 1.0,
                    0.0, 0.0, 1.0
                ],
                "uvs": [
                    0.0, 0.0,
                    1.0, 0.0,
                    1.0, 1.0
                ],
                "faces": [
                    [0, 1, 2]
                ],
                "face_materials": [
                    0
                ]
            }
        ]
    }
    create_response = send_request_with_headers ("POST", url, payload = payload)
    create_response_body = create_response.json ()
    assert create_response.status_code == 200
    assert create_response_body.get ("meshes_created") + create_response_body.get ("meshes_updated") == 1

    get_response = send_request_with_headers (
        "POST",
        f"{base_url}/get-objects",
        payload = { "model_name": "DeleteElementsTestModel" }
    )
    get_response_body = get_response.json ()
    assert get_response.status_code == 200
    assert get_response_body.get ("objects") == [
        {
            "id": "MyElementID",
            "checksum": "MyElementChecksum"
        }
    ]

    delete_response = send_request_with_headers (
        "POST",
        f"{base_url}/delete-objects",
        payload = { "model_name": "DeleteElementsTestModel", "object_ids": ["MyElementID"] }
    )
    assert delete_response.status_code == 200
    delete_response_body = delete_response.json ()
    assert delete_response_body.get ("objects_deleted") == 1

    get_response2 = send_request_with_headers (
        "POST",
        f"{base_url}/get-objects",
        payload = { "model_name": "DeleteElementsTestModel" }
    )
    get_response_body2 = get_response2.json ()
    assert get_response2.status_code == 200
    assert get_response_body2.get ("objects") == []

def create_model (base_url, model_name, object_ids):
    response = send_request_with_headers (
        "POST",
        f"{base_url}/update-meshes",
        payload = make_update_meshes_payload (model_name, [make_triangle_mesh (id) for id in object_ids])
    )
    assert response.status_code == 200
    assert response.json ().get ("meshes_created") == len (object_ids)

def get_object_ids (base_url, model_name):
    response = send_request_with_headers (
        "POST",
        f"{base_url}/get-objects",
        payload = { "model_name": model_name }
    )
    assert response.status_code == 200
    return sorted (obj["id"] for obj in response.json ().get ("objects"))

def test_http_post_delete_objects_unknown_model (base_url):
    response = send_request_with_headers (
        "POST",
        f"{base_url}/delete-objects",
        payload = { "model_name": unique_name ("UnknownModel"), "object_ids": ["ID1"] }
    )
    assert response.status_code == 200
    assert response.json () == { "objects_deleted": 0 }

def test_http_post_delete_objects_unknown_id (base_url):
    model_name = unique_name ("DeleteUnknownIdTestModel")
    create_model (base_url, model_name, ["ID1"])

    response = send_request_with_headers (
        "POST",
        f"{base_url}/delete-objects",
        payload = { "model_name": model_name, "object_ids": ["UnknownID"] }
    )
    assert response.status_code == 200
    assert response.json () == { "objects_deleted": 0 }
    assert get_object_ids (base_url, model_name) == ["ID1"]

def test_http_post_delete_objects_partial (base_url):
    model_name = unique_name ("DeletePartialTestModel")
    create_model (base_url, model_name, ["ID1", "ID2", "ID3"])

    response = send_request_with_headers (
        "POST",
        f"{base_url}/delete-objects",
        payload = { "model_name": model_name, "object_ids": ["ID1", "ID3", "UnknownID"] }
    )
    assert response.status_code == 200
    assert response.json () == { "objects_deleted": 2 }
    assert get_object_ids (base_url, model_name) == ["ID2"]

def test_http_post_delete_objects_twice (base_url):
    model_name = unique_name ("DeleteTwiceTestModel")
    create_model (base_url, model_name, ["ID1"])

    payload = { "model_name": model_name, "object_ids": ["ID1"] }
    first_response = send_request_with_headers ("POST", f"{base_url}/delete-objects", payload = payload)
    assert first_response.status_code == 200
    assert first_response.json () == { "objects_deleted": 1 }

    second_response = send_request_with_headers ("POST", f"{base_url}/delete-objects", payload = payload)
    assert second_response.status_code == 200
    assert second_response.json () == { "objects_deleted": 0 }
