import os
from http_client import send_request_with_headers
from payloads import unique_name, make_triangle_mesh, make_update_meshes_payload

def test_http_post_update_sun (base_url):
    url = f"{base_url}/update-sun"
    payload = {
        "name": "MySunLight",
        "color": [1.0, 0.0, 0.0],
        "energy": 10.0,
        "direction": [-1.0, -1.0, -1.0]
    }
    response = send_request_with_headers ("POST", url, payload = payload)
    response_body = response.json ()
    assert response.status_code == 200
    assert response_body.get ("sun_created") + response_body.get ("sun_updated") == 1

def make_sun_payload (name, energy = 10.0, direction = (-1.0, -1.0, -1.0)):
    return {
        "name": name,
        "color": [1.0, 1.0, 1.0],
        "energy": energy,
        "direction": list (direction)
    }

def update_sun (base_url, payload):
    response = send_request_with_headers ("POST", f"{base_url}/update-sun", payload = payload)
    assert response.status_code == 200
    return response.json ()

def test_http_post_update_sun_existing (base_url):
    name = unique_name ("Sun")

    first_body = update_sun (base_url, make_sun_payload (name, energy = 5.0))
    assert first_body == { "sun_created": 1, "sun_updated": 0 }

    second_body = update_sun (base_url, make_sun_payload (name, energy = 15.0))
    assert second_body == { "sun_created": 0, "sun_updated": 1 }

def test_http_post_update_sun_zero_direction (base_url):
    body = update_sun (base_url, make_sun_payload (unique_name ("Sun"), direction = (0.0, 0.0, 0.0)))
    assert body == { "sun_created": 1, "sun_updated": 0 }

def test_http_post_update_sun_name_used_by_mesh_object (base_url):
    name = unique_name ("SunNameCollision")
    mesh_response = send_request_with_headers (
        "POST",
        f"{base_url}/update-meshes",
        payload = make_update_meshes_payload (unique_name ("SunCollisionTestModel"), [
            make_triangle_mesh ("ID1", name = name)
        ])
    )
    assert mesh_response.status_code == 200
    assert mesh_response.json ().get ("meshes_created") == 1

    body = update_sun (base_url, make_sun_payload (name))
    assert body == { "sun_created": 1, "sun_updated": 0 }
