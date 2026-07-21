import urllib.request
import urllib.error

endpoints = [
    ('http://127.0.0.1:8000/api/v1/scada/registers', 'GET'),
    ('http://127.0.0.1:8000/api/v1/esd/log', 'GET'),
    ('http://127.0.0.1:8000/api/v1/compliance/uploaded-standards', 'GET'),
]

for url, method in endpoints:
    try:
        res = urllib.request.urlopen(url)
        body = res.read().decode()[:120]
        print(f"OK {url} -> {body}")
    except urllib.error.HTTPError as e:
        print(f"ERROR {url} -> {e.code}: {e.read().decode()[:120]}")
    except Exception as e:
        print(f"FAIL {url} -> {e}")
