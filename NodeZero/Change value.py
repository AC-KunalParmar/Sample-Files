import json

# Load the JSON data from a file
with open('/Users/theredhatter/Desktop/ArmorCodeInternship/sample-scan-files-master/NodeZero/NodeZero_Weaknesses_large.json', 'r') as json_file:
    data = json.load(json_file)

# Function to recursively update all occurrences of a field to null
def update_field_to_null(obj, field_name):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == field_name:
                obj[key] = None
            else:
                update_field_to_null(value, field_name)
    elif isinstance(obj, list):
        for item in obj:
            update_field_to_null(item, field_name)

# Change the value of a specific field to null
update_field_to_null(data, "vuln_id")

# Save the modified JSON data back to the file
with open('data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Print a message to confirm the changes
print("Modified JSON data saved to 'data.json'")
