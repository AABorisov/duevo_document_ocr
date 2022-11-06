import http.client
import mimetypes
conn = http.client.HTTPSConnection("127.0.0.1", 8000)
payload = ''
headers = {
  'Authorization': 'Token 34f6d6a72daaed765933699adffc563f006abb86'
}
conn.request("GET", "/api/v1/document/detail/3", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))