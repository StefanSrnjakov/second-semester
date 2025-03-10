#pragma once

#include <fstream>
#include <string>
#include <vector>
#include <functional>
#include <sstream>  // Add this include for istringstream
#include "point.h"  // Include point.h directly

// File operation constants
namespace FileConstants {
    static constexpr size_t MB = 1024 * 1024;
    static constexpr size_t KB = 1024;
    
    // Buffer sizes
    static constexpr size_t READ_BUFFER_SIZE = 1 * MB;
    static constexpr size_t POINTS_PER_WRITE = 4096;
    static constexpr size_t WRITE_BUFFER_SIZE = POINTS_PER_WRITE * sizeof(Point);
    static constexpr size_t CHUNK_SIZE = 1 * MB;
    
    // Progress reporting
    static constexpr size_t PROGRESS_INTERVAL_MB = 10;  // Log every 10MB
    static constexpr double PROGRESS_PERCENTAGE_INTERVAL = 5.0; // Log every 5% of progress
}

// Update callback to use MB processed instead of percentage
using ProgressCallback = std::function<void(size_t points, size_t mb_processed)>;

class FileHandler {
private:
    char* read_buffer_;
    char* write_buffer_;
    std::string binary_file_path_;
    size_t buffer_size_;
    size_t chunk_size_;
    bool owns_binary_file_;
    
    bool parsePoint(const std::string& line, Point& p) {
        std::istringstream iss(line);
        std::string x_str, y_str, z_str;
        
        if (std::getline(iss, x_str, ',') && 
            std::getline(iss, y_str, ',') && 
            std::getline(iss, z_str, ',')) {
            try {
                p.x = std::stod(x_str);
                p.y = std::stod(y_str);
                p.z = std::stod(z_str);
                return true;
            } catch (const std::exception&) {
                return false;
            }
        }
        return false;
    }

public:
    // Original constructor - for creating a new binary file
    FileHandler(const std::string& binary_file_path, 
                size_t buffer_size = FileConstants::READ_BUFFER_SIZE,
                size_t chunk_size = FileConstants::CHUNK_SIZE);
    
    // Constructor for existing binary file - make it more distinct
    // Add a dummy enum to differentiate the constructors
    enum ExistingFileTag { ExistingFile };
    FileHandler(ExistingFileTag, 
                const std::string& binary_file_path,
                size_t total_points,
                size_t buffer_size = FileConstants::READ_BUFFER_SIZE,
                size_t chunk_size = FileConstants::CHUNK_SIZE);
                
    ~FileHandler();

    // CSV operations
    size_t convertCSVToBinary(const std::string& csv_path, 
                             ProgressCallback progress_callback = nullptr);
    
    // Binary file operations
    std::vector<Point> readBinaryChunk(size_t start_point, size_t count);
    void writeBinaryChunk(const std::vector<Point>& points, size_t offset);
    
    // Temp file operations
    void writeTempFile(const std::vector<Point>& points, const std::string& filename);
    std::vector<Point> readTempFile(const std::string& filename, size_t buffer_size);
    void mergeTempFiles(const std::string& file1, const std::string& file2, 
                       const std::string& output, size_t buffer_size);
    
    // File management
    void removeTempFile(const std::string& filename);
    void renameTempFile(const std::string& old_name, const std::string& new_name);
    
    // Add a method to get the total points in the binary file
    size_t getTotalPoints() const;

    // Add this method to get the binary file path
    const std::string& getBinaryFilePath() const {
        return binary_file_path_;
    }

private:
    void initializeBuffers();
    void cleanupBuffers();
}; 