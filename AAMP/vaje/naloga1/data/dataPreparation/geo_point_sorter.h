#pragma once

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>
#include <sstream>
#include <memory>
#include "point.h"  // Include point.h instead of defining Point here

struct Config {
    size_t chunk_size_b;
    std::string input_file_path;
    std::string output_tree_path;
    std::string temp_directory;
    size_t buffer_size_b;
    std::string binary_file_path;

    static Config loadFromFile(const std::string& path);
};

struct TreeNode {
    size_t start;
    size_t stop;
    size_t split;
    double delim;
    bool xy_flag;
    std::string left_child;
    std::string right_child;
};

// Forward declare FileHandler
class FileHandler;

class GeoPointSorter {
private:
    Config config_;
    size_t chunk_size_;
    std::string temp_dir_;
    size_t total_points_;
    size_t total_chunks_;
    size_t points_per_chunk_;
    std::unique_ptr<FileHandler> file_handler_;
    std::string binary_file_path_;
    std::string sorted_output_path_;
    static constexpr size_t POINT_SIZE = sizeof(double) * 3;
    
    void createBinaryFile();
    std::vector<Point> loadChunkFromBinary(size_t start, size_t count);
    void saveChunkToBinary(const std::vector<Point>& points, size_t offset);
    std::vector<Point> loadChunk(std::ifstream& file, size_t start, size_t count);
    void saveChunk(const std::vector<Point>& points, const std::string& filename);
    void mergeSortedFiles(const std::string& file1, const std::string& file2, const std::string& output);
    void mergeSortedChunks(size_t num_chunks);
    void mergePair(const std::string& file1, const std::string& file2, const std::string& output);
    void loadBuffer(std::ifstream& file, std::vector<Point>& buffer, size_t buffer_size);

public:
    GeoPointSorter(const std::string& config_path);
    ~GeoPointSorter();
    void sortOnDisk(bool xy_flag, size_t file_start, size_t file_stop);
    void buildTree();
    const Config& getConfig() const { return config_; }
}; 