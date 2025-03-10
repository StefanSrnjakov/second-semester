#include "geo_point_sorter.h"
#include "file_handler.h"

GeoPointSorter::GeoPointSorter(const std::string& config_path) {
    std::cout << "Loading configuration from: " << config_path << std::endl;
    config_ = Config::loadFromFile(config_path);
    chunk_size_ = config_.chunk_size_b;
    temp_dir_ = config_.temp_directory;
    
    // Initialize the sorted output path
    sorted_output_path_ = temp_dir_ + "sorted_points.bin";
    
    std::cout << "Creating temp directory: " << temp_dir_ << std::endl;
    std::filesystem::create_directories(temp_dir_);
    
    std::string binary_file_path = temp_dir_ + "points.bin";
    
    // Check if binary file already exists
    if (std::filesystem::exists(binary_file_path) && 
        std::filesystem::file_size(binary_file_path) > 0) {
        
        std::cout << "Found existing binary file: " << binary_file_path << std::endl;
        
        // Use the new constructor with the existing binary file
        file_handler_ = std::make_unique<FileHandler>(
            FileHandler::ExistingFile,  // Add the tag
            binary_file_path,
            0,  // We'll get the actual count from the file
            config_.buffer_size_b,
            config_.chunk_size_b
        );
        
        // Get the total points from the file
        total_points_ = file_handler_->getTotalPoints();
        std::cout << "Using existing binary file with " << total_points_ << " points" << std::endl;
        
        // After initializing file_handler_ and getting total_points_
        // Add this line to store the binary file path
        binary_file_path_ = file_handler_->getBinaryFilePath();
    } 
    else {
        std::cout << "Initializing file handler with binary file: " << binary_file_path << std::endl;
        file_handler_ = std::make_unique<FileHandler>(
            binary_file_path,
            config_.buffer_size_b,
            config_.chunk_size_b
        );
        
        // Add this line to store the binary file path
        binary_file_path_ = binary_file_path;
        
        std::cout << "\nStarting CSV to binary conversion..." << std::endl;
        std::cout << "Input file: " << config_.input_file_path << std::endl;
        
        // Convert CSV to binary and get total points
        total_points_ = file_handler_->convertCSVToBinary(
            config_.input_file_path,
            [](size_t points, size_t mb_processed) {
                std::cout << "Processed " << mb_processed << " MB" << std::endl;
            }
        );
    }
    
    // Calculate chunks
    total_chunks_ = (total_points_ * sizeof(Point) + chunk_size_ - 1) / chunk_size_;
    points_per_chunk_ = total_points_ / total_chunks_;
    
    if (points_per_chunk_ == 0) {
        points_per_chunk_ = 1;
        total_chunks_ = total_points_;
    }
    
    std::cout << "\nInitialization complete:" << std::endl;
    std::cout << "Total points: " << total_points_ << std::endl;
    std::cout << "Total chunks: " << total_chunks_ << std::endl;
    std::cout << "Points per chunk: " << points_per_chunk_ << std::endl;
    std::cout << "Chunk size: " << (chunk_size_ / (1024.0 * 1024.0)) << " MB" << std::endl;
    std::cout << "Total data size: " << (total_points_ * sizeof(Point) / (1024.0 * 1024.0)) << " MB" << std::endl;

    // At the end of the constructor, add:
    std::cout << "Binary file path: '" << binary_file_path_ << "'" << std::endl;
}

Config Config::loadFromFile(const std::string& path) {
    Config config;
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Could not open config file");
    }
    
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string key;
        std::getline(iss, key, '=');
        
        key.erase(0, key.find_first_not_of(" \t"));
        key.erase(key.find_last_not_of(" \t") + 1);
        
        std::string value;
        std::getline(iss, value);
        value.erase(0, value.find_first_not_of(" \t"));
        value.erase(value.find_last_not_of(" \t") + 1);
        
        if (key == "chunk_size_b") config.chunk_size_b = std::stoul(value);
        else if (key == "input_file_path") config.input_file_path = value;
        else if (key == "output_tree_path") config.output_tree_path = value;
        else if (key == "temp_directory") config.temp_directory = value;
        else if (key == "buffer_size_b") config.buffer_size_b = std::stoul(value);
    }
    
    return config;
}

std::vector<Point> GeoPointSorter::loadChunkFromBinary(size_t start, size_t count) {
    std::vector<Point> points;
    points.reserve(count);
    
    // Use the correct binary file path
    std::ifstream binary_file(binary_file_path_, std::ios::binary);
    if (!binary_file) {
        throw std::runtime_error("Could not open binary file for reading: " + binary_file_path_);
    }
    
    // Seek to start position
    binary_file.seekg(start * POINT_SIZE);
    
    // Read points
    Point p;
    for (size_t i = 0; i < count && binary_file.read(reinterpret_cast<char*>(&p), POINT_SIZE); ++i) {
        points.push_back(p);
    }
    
    // In the loadChunkFromBinary method, add:
    // std::cout << "Attempting to open binary file: '" << binary_file_path_ << "'" << std::endl;
    
    if (!std::filesystem::exists(binary_file_path_)) {
        throw std::runtime_error("Binary file does not exist: " + binary_file_path_);
    }
    
    return points;
}

void GeoPointSorter::sortOnDisk(bool xy_flag, size_t startPoint, size_t endPoint) {
    std::cout << "\nStarting disk-based sorting..." << std::endl;
    std::cout << "Sorting on " << (xy_flag ? "X" : "Y") << " coordinate" << std::endl;
    std::cout << "Total chunks to process: " << total_chunks_ << std::endl;
    
    // Add timing variables
    auto start_time = std::chrono::high_resolution_clock::now();
    auto last_chunk_start_time = start_time;
    auto last_log_time = start_time;
    
    // Define logging intervals
    const double percentage_interval = 5.0; // Log every 5% progress
    const int time_interval_seconds = 10;   // Also log every 10 seconds
    double last_logged_percentage = 0.0;
    
    for (size_t i = 0; i < total_chunks_; ++i) {
        // Start timing this chunk
        last_chunk_start_time = std::chrono::high_resolution_clock::now();
        
        size_t chunk_start = i * points_per_chunk_;
        size_t chunk_size = std::min(points_per_chunk_, total_points_ - chunk_start);
        
        auto points = loadChunkFromBinary(chunk_start, chunk_size);
        
        std::sort(points.begin(), points.end(),
            [xy_flag](const Point& a, const Point& b) {
                return xy_flag ? a.x < b.x : a.y < b.y;
            });
            
        std::string chunk_file = temp_dir_ + "chunk_" + std::to_string(i);
        saveChunk(points, chunk_file);
        
        // Calculate time taken for this chunk
        auto current_time = std::chrono::high_resolution_clock::now();
        auto chunk_duration = std::chrono::duration_cast<std::chrono::seconds>(
            current_time - last_chunk_start_time).count();
        
        // Calculate progress percentage
        double percentage = (i + 1) * 100.0 / total_chunks_;
        
        // Determine if we should log progress
        bool should_log = false;
        
        // Log based on percentage intervals
        if (percentage >= last_logged_percentage + percentage_interval) {
            should_log = true;
            last_logged_percentage = floor(percentage / percentage_interval) * percentage_interval;
        }
        
        // Also log based on time intervals
        auto time_since_last_log = std::chrono::duration_cast<std::chrono::seconds>(
            current_time - last_log_time).count();
        if (time_since_last_log >= time_interval_seconds) {
            should_log = true;
        }
        
        // Always log the first and last chunk
        if (i == 0 || i == total_chunks_ - 1) {
            should_log = true;
        }
        
        if (should_log) {
            // Calculate remaining time
            size_t chunks_remaining = total_chunks_ - (i + 1);
            
            // Log progress
            std::cout << "Processed chunk " << (i + 1) << "/" << total_chunks_ 
                      << " (" << percentage << "%). " << std::endl;
            last_log_time = current_time;
        }
    }
    
    // Calculate total time
    auto end_time = std::chrono::high_resolution_clock::now();
    auto total_seconds = std::chrono::duration_cast<std::chrono::seconds>(
        end_time - start_time).count();
    
    int hours = total_seconds / 3600;
    int minutes = (total_seconds % 3600) / 60;
    int seconds = total_seconds % 60;
    
    std::cout << "\nAll chunks sorted. Total processing time: ";
    if (hours > 0) std::cout << hours << "h ";
    if (minutes > 0 || hours > 0) std::cout << minutes << "m ";
    std::cout << seconds << "s" << std::endl;
    
    std::cout << "Starting merge phase..." << std::endl;
    mergeSortedChunks(total_chunks_);
}

void GeoPointSorter::mergeSortedChunks(size_t num_chunks) {
    std::cout << "Starting merge phase with " << num_chunks << " chunks" << std::endl;
    size_t chunks_remaining = num_chunks;
    size_t merge_round = 0;
    
    auto merge_start_time = std::chrono::high_resolution_clock::now();
    
    while (chunks_remaining > 1) {
        merge_round++;
        auto round_start_time = std::chrono::high_resolution_clock::now();
        
        size_t pairs = chunks_remaining / 2;
        size_t odd_chunk = chunks_remaining % 2;
        
        std::cout << "Merge round " << merge_round << ": Processing " 
                  << pairs << " pairs of chunks" << std::endl;
        
        for (size_t i = 0; i < pairs; i++) {
            std::string file1 = temp_dir_ + "chunk_" + std::to_string(i * 2);
            std::string file2 = temp_dir_ + "chunk_" + std::to_string(i * 2 + 1);
            std::string output = temp_dir_ + "merged_" + std::to_string(i);
            
            std::cout << "  Merging pair " << (i + 1) << "/" << pairs 
                      << ": " << file1 << " + " << file2 << " -> " << output << std::endl;
            
            mergePair(file1, file2, output);
            
            // Delete merged files
            std::filesystem::remove(file1);
            std::filesystem::remove(file2);
        }
        
        // Handle odd chunk if exists
        if (odd_chunk) {
            std::string old_name = temp_dir_ + "chunk_" + std::to_string(chunks_remaining - 1);
            std::string new_name = temp_dir_ + "merged_" + std::to_string(pairs);
            std::cout << "  Moving odd chunk: " << old_name << " -> " << new_name << std::endl;
            std::filesystem::rename(old_name, new_name);
            pairs++;
        }
        
        // Rename merged files to chunk files for next iteration
        for (size_t i = 0; i < pairs; i++) {
            std::string merged_name = temp_dir_ + "merged_" + std::to_string(i);
            std::string chunk_name = temp_dir_ + "chunk_" + std::to_string(i);
            std::filesystem::rename(merged_name, chunk_name);
        }
        
        chunks_remaining = pairs;
        
        auto round_end_time = std::chrono::high_resolution_clock::now();
        auto round_seconds = std::chrono::duration_cast<std::chrono::seconds>(
            round_end_time - round_start_time).count();
        
        std::cout << "Merge round " << merge_round << " completed in " 
                  << round_seconds << " seconds. Chunks remaining: " 
                  << chunks_remaining << std::endl;
    }
    
    // Rename final chunk to sorted output
    if (chunks_remaining == 1) {
        std::string final_chunk = temp_dir_ + "chunk_0";
        std::cout << "Saving final sorted array to: " << sorted_output_path_ << std::endl;
        std::filesystem::rename(final_chunk, sorted_output_path_);
    }
    
    auto merge_end_time = std::chrono::high_resolution_clock::now();
    auto merge_seconds = std::chrono::duration_cast<std::chrono::seconds>(
        merge_end_time - merge_start_time).count();
    
    std::cout << "Merge phase completed in " << merge_seconds << " seconds" << std::endl;
}

void GeoPointSorter::mergePair(const std::string& file1, const std::string& file2, const std::string& output) {
    std::ifstream in1(file1, std::ios::binary);
    std::ifstream in2(file2, std::ios::binary);
    std::ofstream out(output, std::ios::binary);
    
    if (!in1 || !in2 || !out) {
        throw std::runtime_error("Failed to open files for merging");
    }
    
    // Buffer for reading points
    std::vector<Point> buffer1;
    std::vector<Point> buffer2;
    
    // Calculate buffer size based on config parameters
    // Use points_per_chunk_ which is already calculated based on config
    const size_t BUFFER_SIZE = points_per_chunk_;
    
    std::cout << "  Using buffer size of " << BUFFER_SIZE << " points (" 
              << (BUFFER_SIZE * sizeof(Point) / (1024.0)) << " KB)" << std::endl;
    
    // Read initial buffers
    loadBuffer(in1, buffer1, BUFFER_SIZE);
    loadBuffer(in2, buffer2, BUFFER_SIZE);
    
    size_t pos1 = 0, pos2 = 0;
    std::vector<Point> output_buffer;
    output_buffer.reserve(BUFFER_SIZE);
    
    while (!buffer1.empty() || !buffer2.empty()) {
        while (output_buffer.size() < BUFFER_SIZE && (!buffer1.empty() || !buffer2.empty())) {
            if (buffer1.empty() && !in1.eof()) {
                loadBuffer(in1, buffer1, BUFFER_SIZE);
                pos1 = 0;
            }
            if (buffer2.empty() && !in2.eof()) {
                loadBuffer(in2, buffer2, BUFFER_SIZE);
                pos2 = 0;
            }
            
            if (buffer1.empty() && buffer2.empty()) break;
            
            if (buffer1.empty()) {
                output_buffer.push_back(buffer2[pos2++]);
                if (pos2 >= buffer2.size()) buffer2.clear();
            }
            else if (buffer2.empty()) {
                output_buffer.push_back(buffer1[pos1++]);
                if (pos1 >= buffer1.size()) buffer1.clear();
            }
            else {
                if (buffer1[pos1].x <= buffer2[pos2].x) {
                    output_buffer.push_back(buffer1[pos1++]);
                    if (pos1 >= buffer1.size()) buffer1.clear();
                } else {
                    output_buffer.push_back(buffer2[pos2++]);
                    if (pos2 >= buffer2.size()) buffer2.clear();
                }
            }
        }
        
        // Write output buffer in binary format
        if (!output_buffer.empty()) {
            out.write(reinterpret_cast<const char*>(output_buffer.data()), 
                     output_buffer.size() * sizeof(Point));
            output_buffer.clear();
        }
    }
}

void GeoPointSorter::loadBuffer(std::ifstream& file, std::vector<Point>& buffer, size_t buffer_size) {
    buffer.clear();
    buffer.resize(buffer_size);  // Pre-allocate space
    
    // Read directly into the buffer in binary format
    file.read(reinterpret_cast<char*>(buffer.data()), buffer_size * sizeof(Point));
    
    // Resize to actual number of points read
    size_t points_read = file.gcount() / sizeof(Point);
    buffer.resize(points_read);
}

void GeoPointSorter::saveChunk(const std::vector<Point>& points, const std::string& filename) {
    std::ofstream out(filename, std::ios::binary);
    if (!out) {
        throw std::runtime_error("Could not create output file: " + filename);
    }
    
    // Write the entire vector at once in binary format
    if (!points.empty()) {
        out.write(reinterpret_cast<const char*>(points.data()), points.size() * sizeof(Point));
    }
}

void GeoPointSorter::buildTree() {
    // Now we can use the sorted data to build a tree
    std::cout << "Building tree from sorted data: " << sorted_output_path_ << std::endl;
    
    // Here you would implement the actual tree building logic
    // For now, we'll just create a placeholder output
    std::ofstream output(config_.output_tree_path);
    if (!output) {
        throw std::runtime_error("Could not create tree output file: " + config_.output_tree_path);
    }
    
    output << "{ \"root\": null }" << std::endl;
    
    std::cout << "Tree building complete. Output saved to: " << config_.output_tree_path << std::endl;
}

GeoPointSorter::~GeoPointSorter() = default; 