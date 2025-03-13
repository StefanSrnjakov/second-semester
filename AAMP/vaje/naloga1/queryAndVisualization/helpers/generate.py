import random

def generate_unique_floats(num_rows=200):
    unique_rows = set()
    while len(unique_rows) < num_rows:
        x = round(random.uniform(2000, 2020), 12)
        y = round(random.uniform(1600, 1650), 12)
        z = round(random.uniform(480, 620), 12)
        unique_rows.add((x, y, z))
    return list(unique_rows)

# Generate 200 unique rows
random_floats = generate_unique_floats(200)

# Convert to CSV format
csv_data = "x,y,z,\n" + "\n".join([f"{x},{y},{z}," for x, y, z in random_floats])
print(csv_data)