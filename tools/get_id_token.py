import google.oauth2.id_token

auth_req = google.auth.transport.requests.Request()
service_url = "https://example.com"
id_token = google.oauth2.id_token.fetch_id_token(auth_req, service_url)
print(id_token)
