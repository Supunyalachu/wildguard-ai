import requests

url = "http://127.0.0.1:8000/api/detect/"

image_path = "test.jpg"

with open(image_path, "rb") as image:
    response = requests.post(
        url,
        files={"image": image}
    )

print("Status:", response.status_code)
print("Response:", response.json())