import requests

url = "http://localhost:5000/api/diet/parse-preferences-text"

# Test 1: Simple
response = requests.post(url, json={
    "text": "I'm 30, desk job, want to lose weight, vegan"
})

print("Test 1:")
print(response.json())
print()

# Test 2: With defaults
response2 = requests.post(url, json={
    "text": "I hate onions and love Punjabi food",
    "defaults": {
        "activity_level": "moderately_active",
        "goal": "maintenance",
        "diet_type": "Vegetarian"
    }
})

print("Test 2:")
print(response2.json())
