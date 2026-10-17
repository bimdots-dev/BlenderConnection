import requests
from http_client import send_request_with_headers

def test_http_get_is_alive_with_query_string (base_url):
    response = send_request_with_headers ("GET", f"{base_url}/is-alive?foo=bar")
    assert response.status_code == 200

def test_http_get_not_found_returns_error_body (base_url):
    response = send_request_with_headers ("GET", f"{base_url}/not-found")
    assert response.status_code == 404
    assert response.headers.get ("Content-Type") == "application/json"
    assert response.json () == { "error": "Not found." }

def test_http_get_on_post_endpoint_not_found (base_url):
    response = send_request_with_headers ("GET", f"{base_url}/get-objects")
    assert response.status_code == 404

def test_http_post_not_found (base_url):
    response = send_request_with_headers ("POST", f"{base_url}/not-found", payload = {})
    assert response.status_code == 404
    assert response.json () == { "error": "Not found." }

def test_http_post_on_get_endpoint_not_found (base_url):
    response = send_request_with_headers ("POST", f"{base_url}/is-alive", payload = {})
    assert response.status_code == 404

def test_http_post_invalid_json (base_url):
    response = requests.post (
        f"{base_url}/get-objects",
        data = b"{ this is not json",
        headers = { "Content-Type": "application/json" }
    )
    assert response.status_code == 400
    assert response.json () == { "error": "Request body must be valid JSON." }
