#include "geo_point_sorter.h"

int main([[maybe_unused]] int argc, [[maybe_unused]] char* argv[]) {
    try {
        // Create GeoPointSorter instance with config file
        GeoPointSorter sorter("config.txt");
        
        // For testing, let's sort the entire file by X coordinate first

        sorter.sortOnDisk(true, 50000000, sorter.getTotalPoints());
        
        // Build the tree structure
        // sorter.buildTree();
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
} 