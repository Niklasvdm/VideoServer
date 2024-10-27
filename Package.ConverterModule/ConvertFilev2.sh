#!/bin/bash

# Define an array with file paths, ensure paths are quoted
file_paths=(
    "/Some File/With Spaces/"
    "/Another File/With Spaces/"
    "/Yet Another/File/With Spaces/"
)

# Use a loop to iterate over the elements
for file_path in "${file_paths[@]}"; do
    echo "Checking directory: '$file_path'"  # Debug output
    if [ -d "$file_path" ]; then  # Check if it's a directory
        echo "Listing contents of: $file_path"
        ls "$file_path"
    else
        echo "Error: No such directory: $file_path"
    fi
done