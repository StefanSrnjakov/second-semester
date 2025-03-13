#include "geo_point_sorter.h"

int main([[maybe_unused]] int argc, [[maybe_unused]] char* argv[]) {
    try {
        // Create GeoPointSorter instance with config file
        GeoPointSorter sorter("config.txt");
        
        // Build the tree structure
        // sorter.buildTree();
        sorter.sortOnDisk(0, 100000000, true);
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
} 