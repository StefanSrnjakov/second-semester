#include "file_handler.h"
#include <filesystem>
#include <sstream>
#include <iostream>
#include <chrono>

FileHandler::FileHandler(const std::string& binary_file_path, 
                        size_t buffer_size,
                        size_t chunk_size)
    : binary_file_path_(binary_file_path),
      buffer_size_(buffer_size),
      chunk_size_(chunk_size),
      owns_binary_file_(true) {
    initializeBuffers();
}

FileHandler::FileHandler(ExistingFileTag, 
                        const std::string& binary_file_path,
                        size_t buffer_size,
                        size_t chunk_size)
    : binary_file_path_(binary_file_path),
      buffer_size_(buffer_size),
      chunk_size_(chunk_size),
      owns_binary_file_(false) {
    
    initializeBuffers();
    
    // Verify the binary file exists and has the expected size
    std::ifstream file(binary_file_path, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot open binary file: " + binary_file_path);
    }
    
    file.seekg(0, std::ios::end);
    size_t file_size = file.tellg();
    
    std::cout << "Using existing binary file: " << binary_file_path << std::endl;
    std::cout << "File size: " << (file_size / (1024.0 * 1024.0)) << " MB" << std::endl;
    size_t total_points = file_size / sizeof(Point);
    std::cout << "Total points: " << total_points << std::endl;
}

FileHandler::~FileHandler() {
    cleanupBuffers();
}

void FileHandler::initializeBuffers() {
    read_buffer_ = new char[buffer_size_];
    write_buffer_ = new char[FileConstants::WRITE_BUFFER_SIZE];
}

void FileHandler::cleanupBuffers() {
    delete[] read_buffer_;
    delete[] write_buffer_;
}

size_t FileHandler::convertCSVToBinary(const std::string& csv_path, 
                                     ProgressCallback progress_callback) {
    std::cout << "Opening input file: " << csv_path << std::endl;
    std::ifstream input_file(csv_path);
    
    // Use the buffer_size_ member variable
    input_file.rdbuf()->pubsetbuf(read_buffer_, buffer_size_);
    
    // Get file size for progress tracking
    input_file.seekg(0, std::ios::end);
    const size_t file_size = input_file.tellg();
    input_file.seekg(0);
    std::cout << "Input file size: " << (file_size / (1024.0 * 1024.0)) << " MB" << std::endl;
    
    std::cout << "Creating binary file: " << binary_file_path_ << std::endl;
    std::ofstream binary_file(binary_file_path_, std::ios::binary | std::ios::trunc);
    binary_file.rdbuf()->pubsetbuf(write_buffer_, FileConstants::WRITE_BUFFER_SIZE);
    
    if (!input_file || !binary_file) {
        throw std::runtime_error("Failed to open files for conversion");
    }
    
    size_t total_points = 0;
    size_t bytes_processed = 0;
    size_t last_progress_mb = 0;
    std::vector<Point> points_buffer;
    points_buffer.reserve(FileConstants::POINTS_PER_WRITE);
    
    // Use the chunk_size_ member variable
    std::vector<char> chunk_buffer(chunk_size_);
    std::string leftover;
    
    // Add timing variables
    auto start_time = std::chrono::high_resolution_clock::now();
    auto last_progress_time = start_time;
    
    std::cout << "Starting conversion process..." << std::endl;
    
    while (input_file) {
        // Read directly into buffer - faster than string operations
        input_file.read(chunk_buffer.data(), chunk_buffer.size());
        size_t bytes_read = input_file.gcount();
        if (bytes_read == 0) break;
        
        bytes_processed += bytes_read;
        
        // Process the chunk more efficiently
        char* chunk_start = chunk_buffer.data();
        char* chunk_end = chunk_start + bytes_read;
        char* line_start = chunk_start;
        
        // Process any leftover data from previous chunk
        if (!leftover.empty()) {
            // Process leftover + beginning of current chunk until newline
            for (char* pos = chunk_start; pos < chunk_end; ++pos) {
                if (*pos == '\n') {
                    // Found a newline - process the complete line
                    leftover.append(chunk_start, pos - chunk_start + 1);
                    Point p;
                    if (parsePoint(leftover, p)) {
                        points_buffer.push_back(p);
                        total_points++;
                    }
                    leftover.clear();
                    line_start = pos + 1;
                    break;
                }
            }
            
            // If no newline found, append entire chunk to leftover
            if (!leftover.empty()) {
                leftover.append(chunk_start, bytes_read);
                continue;
            }
        }
        
        // Process complete lines within the current chunk
        for (char* pos = line_start; pos < chunk_end; ++pos) {
            if (*pos == '\n') {
                // Process the line
                std::string line(line_start, pos - line_start + 1);
                if (!line.empty()) {
                    Point p;
                    if (parsePoint(line, p)) {
                        points_buffer.push_back(p);
                        total_points++;
                    }
                }
                line_start = pos + 1;
                
                // Batch write when buffer is full
                if (points_buffer.size() >= FileConstants::POINTS_PER_WRITE) {
                    binary_file.write(reinterpret_cast<const char*>(points_buffer.data()), 
                                     points_buffer.size() * sizeof(Point));
                    points_buffer.clear();
                }
            }
        }
        
        // Save any incomplete line for next iteration
        if (line_start < chunk_end) {
            leftover.assign(line_start, chunk_end - line_start);
        }
        
        // Report progress based on both MB and percentage
        size_t mb_processed = bytes_processed / (1024 * 1024);
        double percentage = bytes_processed * 100.0 / file_size;
        
        // Log if we've processed another interval of MB or percentage
        bool should_log = false;
        if (mb_processed % FileConstants::PROGRESS_INTERVAL_MB == 0 && mb_processed != last_progress_mb) {
            should_log = true;
            last_progress_mb = mb_processed;
        }
        
        // Also log based on percentage intervals
        static double last_percentage = 0.0;
        if (percentage >= last_percentage + FileConstants::PROGRESS_PERCENTAGE_INTERVAL) {
            should_log = true;
            last_percentage = floor(percentage / FileConstants::PROGRESS_PERCENTAGE_INTERVAL) * 
                              FileConstants::PROGRESS_PERCENTAGE_INTERVAL;
        }
        
        if (progress_callback && should_log) {
            auto current_time = std::chrono::high_resolution_clock::now();
            auto time_elapsed = std::chrono::duration_cast<std::chrono::seconds>(
                current_time - last_progress_time).count();
            
            // Calculate estimated time remaining
            
            std::cout << "Processed " << mb_processed << " MB (" 
                      << percentage << "%). "
                      << "Time elapsed: " << time_elapsed << "s. ";                      
            
            last_progress_time = current_time;
            
            progress_callback(total_points, mb_processed);
        }
    }
    
    // Process any final leftover data
    if (!leftover.empty()) {
        Point p;
        if (parsePoint(leftover, p)) {
            points_buffer.push_back(p);
            total_points++;
        }
    }
    
    // Write any remaining points
    if (!points_buffer.empty()) {
        binary_file.write(reinterpret_cast<const char*>(points_buffer.data()), 
                         points_buffer.size() * sizeof(Point));
    }
    
    std::cout << "\nConversion completed:" << std::endl;
    std::cout << "Total points processed: " << total_points << std::endl;
    std::cout << "Binary file size: " << (binary_file.tellp() / (1024.0 * 1024.0)) << " MB" << std::endl;
    
    // Add total processing time at the end
    auto end_time = std::chrono::high_resolution_clock::now();
    auto total_seconds = std::chrono::duration_cast<std::chrono::seconds>(
        end_time - start_time).count();
    int hours = total_seconds / 3600;
    int minutes = (total_seconds % 3600) / 60;
    int seconds = total_seconds % 60;
    
    std::cout << "Total processing time: ";
    if (hours > 0) std::cout << hours << "h ";
    if (minutes > 0 || hours > 0) std::cout << minutes << "m ";
    std::cout << seconds << "s" << std::endl;
    
    return total_points;
}

// Add a method to get the total points
size_t FileHandler::getTotalPoints() const {
    std::ifstream file(binary_file_path_, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot open binary file to get total points");
    }
    
    file.seekg(0, std::ios::end);
    size_t file_size = file.tellg();
    return file_size / sizeof(Point);
}

void FileHandler::convertBinaryToCSV(const std::string& output_csv_path, 
                                   ProgressCallback progress_callback) {
    std::cout << "Opening binary file: " << binary_file_path_ << std::endl;
    std::ifstream binary_file(binary_file_path_, std::ios::binary);
    binary_file.rdbuf()->pubsetbuf(read_buffer_, buffer_size_);
    
    if (!binary_file) {
        throw std::runtime_error("Could not open binary file: " + binary_file_path_);
    }
    
    // Create the sorted directory if it doesn't exist
    std::filesystem::create_directories("sorted");
    
    std::cout << "Creating CSV file: " << output_csv_path << std::endl;
    std::ofstream csv_file(output_csv_path);
    csv_file.rdbuf()->pubsetbuf(write_buffer_, FileConstants::WRITE_BUFFER_SIZE);
    
    if (!csv_file) {
        throw std::runtime_error("Could not create CSV file: " + output_csv_path);
    }
    
    // Get file size for progress tracking
    binary_file.seekg(0, std::ios::end);
    const size_t file_size = binary_file.tellg();
    binary_file.seekg(0);
    
    std::cout << "Binary file size: " << (file_size / (1024.0 * 1024.0)) << " MB" << std::endl;
    
    size_t bytes_processed = 0;
    size_t last_progress_mb = 0;
    const size_t BUFFER_SIZE = chunk_size_ / sizeof(Point);
    std::vector<Point> points_buffer(BUFFER_SIZE);
    
    auto start_time = std::chrono::high_resolution_clock::now();
    auto last_progress_time = start_time;
    
    std::cout << "Starting conversion process..." << std::endl;
    
    // Use stringstream for efficient string operations
    std::stringstream line_buffer;
    line_buffer.precision(10);  // Increase precision
    line_buffer << std::fixed;  // Use fixed notation
    
    while (binary_file) {
        // Read chunk of points
        binary_file.read(reinterpret_cast<char*>(points_buffer.data()), 
                        BUFFER_SIZE * sizeof(Point));
        size_t points_read = binary_file.gcount() / sizeof(Point);
        if (points_read == 0) break;
        
        bytes_processed += points_read * sizeof(Point);
        
        // Convert points to CSV format
        for (size_t i = 0; i < points_read; ++i) {
            const Point& p = points_buffer[i];
            line_buffer << p.x << "," << p.y << "," << p.z << "\n";
            
            // Flush the buffer periodically to avoid memory buildup
            if (i % 10000 == 0) {
                csv_file << line_buffer.str();
                line_buffer.str("");
                line_buffer.clear();
            }
        }
        
        // Write any remaining data
        csv_file << line_buffer.str();
        line_buffer.str("");
        line_buffer.clear();
        
        // Progress reporting
        size_t mb_processed = bytes_processed / (1024 * 1024);
        double percentage = bytes_processed * 100.0 / file_size;
        
        bool should_log = false;
        if (mb_processed % FileConstants::PROGRESS_INTERVAL_MB == 0 && 
            mb_processed != last_progress_mb) {
            should_log = true;
            last_progress_mb = mb_processed;
        }
        
        static double last_percentage = 0.0;
        if (percentage >= last_percentage + FileConstants::PROGRESS_PERCENTAGE_INTERVAL) {
            should_log = true;
            last_percentage = floor(percentage / FileConstants::PROGRESS_PERCENTAGE_INTERVAL) * 
                            FileConstants::PROGRESS_PERCENTAGE_INTERVAL;
        }
        
        if (progress_callback && should_log) {
            auto current_time = std::chrono::high_resolution_clock::now();
            auto time_elapsed = std::chrono::duration_cast<std::chrono::seconds>(
                current_time - last_progress_time).count();
            
            std::cout << "Processed " << mb_processed << " MB (" 
                     << percentage << "%). "
                     << "Time elapsed: " << time_elapsed << "s. " << std::endl;
            
            last_progress_time = current_time;
            progress_callback(points_read, mb_processed);
        }
    }
    
    // Report final statistics
    auto end_time = std::chrono::high_resolution_clock::now();
    auto total_seconds = std::chrono::duration_cast<std::chrono::seconds>(
        end_time - start_time).count();
    
    std::cout << "\nConversion completed:" << std::endl;
    std::cout << "Total bytes processed: " << bytes_processed << std::endl;
    std::cout << "CSV file size: " << (std::filesystem::file_size(output_csv_path) / 
                                     (1024.0 * 1024.0)) << " MB" << std::endl;
    
    int hours = total_seconds / 3600;
    int minutes = (total_seconds % 3600) / 60;
    int seconds = total_seconds % 60;
    
    std::cout << "Total processing time: ";
    if (hours > 0) std::cout << hours << "h ";
    if (minutes > 0 || hours > 0) std::cout << minutes << "m ";
    std::cout << seconds << "s" << std::endl;
}
