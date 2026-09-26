import requests

def send_request_with_headers (method, url, payload = None):
    headers = { "Content-Type": "application/json" }
    return requests.request (
        method = method,
        url = url,
        json = payload,
        headers = headers
    )
