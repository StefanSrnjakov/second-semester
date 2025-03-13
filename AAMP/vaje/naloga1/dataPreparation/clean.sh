#!/bin/bash

# Remove object files and executable
rm -f *.o
rm -f geo_point_sorter

# Clean temp directory
rm -rf temp/*
rm -rf tempCsv/*
# Remove any backup files that editors might create
rm -f *~
rm -f *.bak

echo "Cleaned build files and temp directory" 