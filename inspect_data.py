import pickle
from pprint import pprint

# Path to your .dat file
path = "data/university_data.dat"   # adjust if in a different folder

with open(path, "rb") as f:
    data = pickle.load(f)

print("Data file loaded successfully!\n")

# Check the overall structure
print("Data type:", type(data))
if isinstance(data, dict):
    print("Top-level keys:", list(data.keys()))

# Pretty print the contents
print("\n--- RAW DATA ---")
pprint(data, width=100)

# If your data is an object (like a custom DataStore), try printing internal details
if hasattr(data, "__dict__"):
    print("\n--- OBJECT ATTRIBUTES ---")
    pprint(data.__dict__, width=100)