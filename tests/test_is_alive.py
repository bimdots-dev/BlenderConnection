from http_client import send_request_with_headers

def test_http_get_is_alive (base_url):
    response = send_request_with_headers ("GET", f"{base_url}/is-alive")
    assert response.status_code == 200
    assert response.json () == {
        "version": "1.5.0"
    }

def test_http_get_not_found (base_url):
    response = send_request_with_headers ("GET", f"{base_url}/not-found")
    assert response.status_code == 404
