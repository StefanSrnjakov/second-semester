{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "vscode": {
     "languageId": "plaintext"
    }
   },
   "outputs": [],
   "source": [
    "import random\n",
    "\n",
    "def generate_unique_floats(num_rows=200):\n",
    "    unique_rows = set()\n",
    "    while len(unique_rows) < num_rows:\n",
    "        x = round(random.uniform(2000, 2020), 12)\n",
    "        y = round(random.uniform(1600, 1650), 12)\n",
    "        z = round(random.uniform(480, 620), 12)\n",
    "        unique_rows.add((x, y, z))\n",
    "    return list(unique_rows)\n",
    "\n",
    "# Generate 200 unique rows\n",
    "random_floats = generate_unique_floats(200)\n",
    "\n",
    "# Convert to CSV format\n",
    "csv_data = \"x,y,z,\\n\" + \"\\n\".join([f\"{x},{y},{z},\" for x, y, z in random_floats])\n",
    "csv_data"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
