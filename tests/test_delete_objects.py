import os
from http_client import send_request_with_headers

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
