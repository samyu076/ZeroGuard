import urllib.request
import urllib.error

try:
    res = urllib.request.urlopen('http://127.0.0.1:8000/api/v1/metrics')
    print("Success:", res.read().decode())
except urllib.error.HTTPError as e:
    print("Code:", e.code)
    print("Body:", e.read().decode())
