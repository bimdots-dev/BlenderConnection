import os
from http_client import send_request_with_headers

def test_http_post_update_meshes (base_url):
    url = f"{base_url}/update-meshes"
    texture_file_location = os.path.join (os.path.dirname (__file__), "test_files", "texture.png")
    payload = {
        "model_name": "UpdateMeshesTestModel",
        "materials": [
            {
                "name": "Red",
                "color": [1.0, 0.0, 0.0],
                "metallic": 0.0,
                "roughness": 0.5,
                "alpha": 0.8
            },
            {
                "name": "Green",
                "color": [0.0, 1.0, 0.0],
                "metallic": 0.0,
                "roughness": 0.5,
                "alpha": 1.0,
                "texture": {
                    "file_path": texture_file_location,
                    "scale": [1.0, 1.0],
                    "rotation": 0.0
                }
            }
        ],
        "meshes": [
            {
                "id": "6d326053-f31a-4464-bfe0-2d15aec5f382",
                "name": "MyElement",
                "checksum": "abc123",
                "location": [0, 0, 0],
                "vertices": [
                    0.0, 0.0, 0.0,
                    1.0, 0.0, 0.0,
                    1.0, 1.0, 0.0,
                    0.0, 1.0, 0.0
                ],
                "normals": [
                    0.0, 0.0, 1.0,
                    0.0, 0.0, 1.0,
                    0.0, 0.0, 1.0,
                    0.0, 0.0, 1.0,
                    0.0, 0.0, 1.0,
                    0.0, 0.0, 1.0
                ],
                "uvs": [
                    0.0, 0.0,
                    1.0, 0.0,
                    1.0, 1.0,
                    0.0, 0.0,
                    1.0, 1.0,
                    0.0, 1.0
                ],
                "faces": [
                    [0, 1, 2],
                    [0, 2, 3]
                ],
                "face_materials": [
                    0,
                    1
                ]
            }
        ]
    }
    response = send_request_with_headers ("POST", url, payload = payload)
    response_body = response.json ()
    assert response.status_code == 200
    assert response_body.get ("meshes_created") + response_body.get ("meshes_updated") == 1
