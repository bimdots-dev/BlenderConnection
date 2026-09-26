import os
from http_client import send_request_with_headers

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
