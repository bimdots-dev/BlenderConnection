import pytest
import os
from http_client import send_request_with_headers
from payloads import unique_name, make_material, make_triangle_mesh, make_quad_mesh, make_mesh_with_faces, make_update_meshes_payload

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

def update_meshes (base_url, payload):
    response = send_request_with_headers ("POST", f"{base_url}/update-meshes", payload = payload)
    assert response.status_code == 200
    return response.json ()

def get_objects (base_url, model_name):
    response = send_request_with_headers (
        "POST",
        f"{base_url}/get-objects",
        payload = { "model_name": model_name }
    )
    assert response.status_code == 200
    return sorted (response.json ().get ("objects"), key = lambda obj: obj["id"])

def test_http_post_update_meshes_existing_mesh (base_url):
    model_name = unique_name ("UpdateExistingMeshTestModel")

    first_body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_triangle_mesh ("ID1", checksum = "Checksum1")
    ]))
    assert first_body.get ("meshes_created") == 1
    assert first_body.get ("meshes_updated") == 0

    second_body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_triangle_mesh ("ID1", checksum = "Checksum2")
    ]))
    assert second_body.get ("meshes_created") == 0
    assert second_body.get ("meshes_updated") == 1

    assert get_objects (base_url, model_name) == [
        { "id": "ID1", "checksum": "Checksum2" }
    ]

def test_http_post_update_meshes_create_and_update_in_one_request (base_url):
    model_name = unique_name ("CreateAndUpdateMeshTestModel")
    update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_triangle_mesh ("ID1", checksum = "Checksum1")
    ]))

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_triangle_mesh ("ID1", checksum = "Checksum1b"),
        make_triangle_mesh ("ID2", checksum = "Checksum2")
    ]))
    assert body.get ("meshes_created") == 1
    assert body.get ("meshes_updated") == 1

    assert get_objects (base_url, model_name) == [
        { "id": "ID1", "checksum": "Checksum1b" },
        { "id": "ID2", "checksum": "Checksum2" }
    ]

def test_http_post_update_meshes_same_id_in_different_models (base_url):
    model_name1 = unique_name ("SameIdTestModel1")
    model_name2 = unique_name ("SameIdTestModel2")

    body1 = update_meshes (base_url, make_update_meshes_payload (model_name1, [
        make_triangle_mesh ("ID1", checksum = "Checksum1")
    ]))
    body2 = update_meshes (base_url, make_update_meshes_payload (model_name2, [
        make_triangle_mesh ("ID1", checksum = "Checksum2")
    ]))
    assert body1.get ("meshes_created") == 1
    assert body2.get ("meshes_created") == 1

    assert get_objects (base_url, model_name1) == [{ "id": "ID1", "checksum": "Checksum1" }]
    assert get_objects (base_url, model_name2) == [{ "id": "ID1", "checksum": "Checksum2" }]

def test_http_post_update_meshes_reuses_existing_material (base_url):
    model_name = unique_name ("ReuseMaterialTestModel")
    materials = [make_material (unique_name ("Material"))]

    first_body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_triangle_mesh ("ID1")
    ], materials = materials))
    assert first_body.get ("materials_created") == 1

    second_body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_triangle_mesh ("ID2")
    ], materials = materials))
    assert second_body.get ("materials_created") == 0
    assert second_body.get ("meshes_created") == 1

def test_http_post_update_meshes_material_shared_by_faces_created_once (base_url):
    model_name = unique_name ("SharedMaterialTestModel")
    materials = [make_material (unique_name ("Material"))]

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_quad_mesh ("ID1", face_materials = (0, 0)),
        make_triangle_mesh ("ID2", material_index = 0)
    ], materials = materials))
    assert body.get ("materials_created") == 1
    assert body.get ("meshes_created") == 2

def test_http_post_update_meshes_multiple_materials (base_url):
    model_name = unique_name ("MultipleMaterialsTestModel")
    materials = [
        make_material (unique_name ("Unused"), color = (0.0, 0.0, 1.0)),
        make_material (unique_name ("Red"), color = (1.0, 0.0, 0.0)),
        make_material (unique_name ("Green"), color = (0.0, 1.0, 0.0), alpha = 0.5)
    ]

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_quad_mesh ("ID1", face_materials = (1, 2))
    ], materials = materials))
    assert body.get ("materials_created") == 2
    assert body.get ("meshes_created") == 1

def test_http_post_update_meshes_invalid_texture_path (base_url):
    model_name = unique_name ("InvalidTextureTestModel")
    materials = [
        make_material (unique_name ("Textured"), texture = {
            "file_path": os.path.join (os.path.dirname (__file__), "test_files", "does_not_exist.png"),
            "scale": [1.0, 1.0],
            "rotation": 0.0
        })
    ]

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_triangle_mesh ("ID1")
    ], materials = materials))
    assert body.get ("materials_created") == 1
    assert body.get ("meshes_created") == 1

def test_http_post_update_meshes_empty_mesh_list (base_url):
    model_name = unique_name ("EmptyMeshListTestModel")
    body = update_meshes (base_url, make_update_meshes_payload (model_name, []))
    assert body == {
        "materials_created": 0,
        "meshes_created": 0,
        "meshes_updated": 0
    }
    assert get_objects (base_url, model_name) == []

def test_http_post_update_meshes_normal_count_mismatch (base_url):
    model_name = unique_name ("NormalMismatchTestModel")
    mesh = make_triangle_mesh ("ID1")
    mesh["normals"] = mesh["normals"][:-3]

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [mesh]))
    assert body.get ("meshes_created") == 0
    assert body.get ("meshes_updated") == 0
    assert get_objects (base_url, model_name) == []

def test_http_post_update_meshes_uv_count_mismatch (base_url):
    model_name = unique_name ("UvMismatchTestModel")
    mesh = make_triangle_mesh ("ID1")
    mesh["uvs"] = mesh["uvs"] + [0.5, 0.5]

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [mesh]))
    assert body.get ("meshes_created") == 0
    assert body.get ("meshes_updated") == 0
    assert get_objects (base_url, model_name) == []

def test_http_post_update_meshes_face_material_count_mismatch (base_url):
    model_name = unique_name ("FaceMaterialMismatchTestModel")
    mesh = make_triangle_mesh ("ID1")
    mesh["face_materials"] = [0, 0]

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [mesh]))
    assert body.get ("meshes_created") == 0
    assert body.get ("meshes_updated") == 0
    assert get_objects (base_url, model_name) == []

def test_http_post_update_meshes_invalid_mesh_does_not_block_others (base_url):
    model_name = unique_name ("PartialInvalidTestModel")
    invalid_mesh = make_triangle_mesh ("InvalidID")
    invalid_mesh["normals"] = []

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_triangle_mesh ("ValidID1", checksum = "Checksum1"),
        invalid_mesh,
        make_triangle_mesh ("ValidID2", checksum = "Checksum2")
    ]))
    assert body.get ("meshes_created") == 2
    assert get_objects (base_url, model_name) == [
        { "id": "ValidID1", "checksum": "Checksum1" },
        { "id": "ValidID2", "checksum": "Checksum2" }
    ]

@pytest.mark.parametrize ("faces", [
    [[0, 1, 1, 2]],
    [[0, 1, 2, 2]],
    [[0, 1, 2, 0]],
    [[0, 1, 0, 2]],
    [[0, 0, 0]],
    [[0, 1, 2], [0, 2, 2, 3]],
    [[0, 1, 4]],
    [[0, 1, -1]],
    [[0, 1]],
    [[]],
    [[0, 1, 2], [2, 1, 0]]
], ids = [
    "repeated_consecutive_vertex",
    "repeated_last_vertex",
    "repeated_first_and_last_vertex",
    "repeated_non_consecutive_vertex",
    "all_vertices_same",
    "invalid_second_face",
    "vertex_index_out_of_range",
    "negative_vertex_index",
    "less_than_three_vertices",
    "empty_face",
    "duplicate_face"
])
def test_http_post_update_meshes_invalid_face (base_url, faces):
    model_name = unique_name ("InvalidFaceTestModel")

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_mesh_with_faces ("ID1", faces)
    ]))
    assert body.get ("meshes_created") == 0
    assert body.get ("meshes_updated") == 0
    assert get_objects (base_url, model_name) == []

def test_http_post_update_meshes_invalid_face_does_not_block_others (base_url):
    model_name = unique_name ("PartialInvalidFaceTestModel")

    body = update_meshes (base_url, make_update_meshes_payload (model_name, [
        make_mesh_with_faces ("ValidID1", [[0, 1, 2, 3]], checksum = "Checksum1"),
        make_mesh_with_faces ("InvalidID1", [[0, 1, 1, 2]]),
        make_mesh_with_faces ("InvalidID2", [[0, 1, 7]]),
        make_mesh_with_faces ("ValidID2", [[0, 1, 2], [0, 2, 3]], checksum = "Checksum2")
    ]))
    assert body.get ("meshes_created") == 2
    assert get_objects (base_url, model_name) == [
        { "id": "ValidID1", "checksum": "Checksum1" },
        { "id": "ValidID2", "checksum": "Checksum2" }
    ]