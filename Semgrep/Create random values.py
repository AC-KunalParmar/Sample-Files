import json
import random

# Your JSON data
with open('/Users/theredhatter/Desktop/ArmorCodeInternship/sample-scan-files-master/Semgrep/Untitled-1.json', 'r') as file:
    data = json.load(file)

# Function to generate a random integer ID
def generate_random_id():
    return random.randint(100000, 999999)

# Update the "id" field for each project in the JSON data
for project in data["projects"]:
    project["id"] = generate_random_id()

# Convert the updated data back to JSON
updated_json = json.dumps(data, indent=4)

with open('output.json', 'w') as file:
    json.dump(data, file, indent=4)
# Print the updated JSON
#print(updated_json)
