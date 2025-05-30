import requests

url = "https://api.binance.tr"
pem_path = "...cert.pem" 
try:
    response = requests.get(url, verify=pem_path)
    print("✅ Success Certcertificate Status code:", response.status_code)
    print("Response:", response.text[:200]) 
except requests.exceptions.SSLError as ssl_err:
    print("❌ SSL Certificate Error:", ssl_err)
except Exception as e:
    print("❌ Response Error:", e)
