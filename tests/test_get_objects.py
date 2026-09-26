import os
from http_client import send_request_with_headers

def test_http_post_get_objects (base_url):
    url = f"{base_url}/update-meshes"
    payload = {
        "model_name": "GetElementsTestModel",
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
        payload = { "model_name": "GetElementsTestModel" }
    )
    get_response_body = get_response.json ()
    assert get_response.status_code == 200
    assert get_response_body.get ("objects") == [
        {
            "id": "MyElementID",
            "checksum": "MyElementChecksum"
        }
    ]
