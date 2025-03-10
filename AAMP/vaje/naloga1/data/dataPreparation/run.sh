#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p temp

# Build the project
make clean && make

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful. Running program..."
    ./geo_point_sorter
else
    echo "Build failed!"
    exit 1
fi 