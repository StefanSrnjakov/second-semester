#include "geo_point_sorter.h"
#include "file_handler.h"
#include <queue>
#include <map>

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
    
    // Calculate the range to sort
    size_t range_size = endPoint - startPoint;
    if (range_size == 0 || startPoint >= total_points_ || endPoint > total_points_) {
        throw std::runtime_error("Invalid range for sorting: " + 
                                std::to_string(startPoint) + " to " + 
                                std::to_string(endPoint));
    }
    
    std::cout << "Sorting points from " << startPoint << " to " << endPoint 
              << " (" << range_size << " points, " 
              << (range_size * sizeof(Point) / (1024.0 * 1024.0)) << " MB)" << std::endl;
    
    // Calculate chunks for this range
    size_t range_chunks = (range_size * sizeof(Point) + chunk_size_ - 1) / chunk_size_;
    size_t points_per_range_chunk = range_size / range_chunks;
    
    if (points_per_range_chunk == 0) {
        points_per_range_chunk = 1;
        range_chunks = range_size;
    }
    
    std::cout << "Total chunks to process: " << range_chunks << std::endl;
    
    // Add timing variables
    auto start_time = std::chrono::high_resolution_clock::now();
    auto last_chunk_start_time = start_time;
    auto last_log_time = start_time;
    
    // Define logging intervals
    const double percentage_interval = 5.0; // Log every 5% progress
    const int time_interval_seconds = 10;   // Also log every 10 seconds
    double last_logged_percentage = 0.0;
    
    // Process each chunk in the range
    for (size_t i = 0; i < range_chunks; ++i) {
        // Start timing this chunk
        last_chunk_start_time = std::chrono::high_resolution_clock::now();
        
        // Calculate the actual points for this chunk
        size_t chunk_start = startPoint + i * points_per_range_chunk;
        size_t chunk_size = std::min(points_per_range_chunk, endPoint - chunk_start);
        
        // Load the chunk from binary file
        auto points = loadChunkFromBinary(chunk_start, chunk_size);
        
        // Sort the chunk based on the specified dimension
        std::sort(points.begin(), points.end(),
            [xy_flag](const Point& a, const Point& b) {
                return xy_flag ? a.x < b.x : a.y < b.y;
            });
            
        // Save the sorted chunk to a temporary file
        std::string chunk_file = temp_dir_ + "chunk_" + std::to_string(i);
        saveChunk(points, chunk_file);
        
        // Calculate time taken for this chunk
        auto current_time = std::chrono::high_resolution_clock::now();
        auto chunk_duration = std::chrono::duration_cast<std::chrono::seconds>(
            current_time - last_chunk_start_time).count();
        
        // Calculate progress percentage
        double percentage = (i + 1) * 100.0 / range_chunks;
        
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
        if (i == 0 || i == range_chunks - 1) {
            should_log = true;
        }
        
        if (should_log) {
            // Log progress
            std::cout << "Processed chunk " << (i + 1) << "/" << range_chunks 
                      << " (" << percentage << "%). " << std::endl;
            last_log_time = current_time;
        }
    }
    
    // Merge the sorted chunks
    mergeSortedChunks(range_chunks);
    
    // Calculate total time
    auto end_time = std::chrono::high_resolution_clock::now();
    auto total_seconds = std::chrono::duration_cast<std::chrono::seconds>(
        end_time - start_time).count();
    
    int hours = total_seconds / 3600;
    int minutes = (total_seconds % 3600) / 60;
    int seconds = total_seconds % 60;
    
    std::cout << "Sorting completed in ";
    if (hours > 0) std::cout << hours << "h ";
    if (minutes > 0 || hours > 0) std::cout << minutes << "m ";
    std::cout << seconds << "s" << std::endl;
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

// Main tree building function
void GeoPointSorter::buildTree() {
    std::cout << "Building KD-tree from binary data..." << std::endl;
    
    // Initialize tree building parameters
    initializeTreeBuilding();
    
    // Build the tree structure
    std::map<std::string, TreeNode> tree_nodes = buildTreeStructure();
    
    // Write the tree to file
    writeTreeToFile(tree_nodes);
    
    std::cout << "Tree building complete. Output saved to: " << config_.output_tree_path << std::endl;
    std::cout << "Created " << tree_nodes.size() << " nodes" << std::endl;
}

// Initialize parameters for tree building
void GeoPointSorter::initializeTreeBuilding() {
    // Create the output file for the tree
    std::ofstream tree_file(config_.output_tree_path);
    if (!tree_file) {
        throw std::runtime_error("Could not create tree output file: " + config_.output_tree_path);
    }
    
    // Define the minimum partition size (5MB)
    const size_t MIN_PARTITION_SIZE_BYTES = 5 * 1024 * 1024;
    min_partition_points_ = MIN_PARTITION_SIZE_BYTES / sizeof(Point);
    
    std::cout << "Total points: " << total_points_ << std::endl;
    std::cout << "Minimum partition size: " << min_partition_points_ << " points ("
              << (MIN_PARTITION_SIZE_BYTES / (1024.0 * 1024.0)) << " MB)" << std::endl;
}

// Build the tree structure using breadth-first traversal
std::map<std::string, TreeNode> GeoPointSorter::buildTreeStructure() {
    // Create the root node
    TreeNode root;
    root.start = 0;
    root.stop = total_points_;
    root.xy_flag = true; // Start with X dimension
    
    // Queue for breadth-first tree construction
    std::queue<TreeNode> node_queue;
    node_queue.push(root);
    
    // Map to store all nodes
    std::map<std::string, TreeNode> tree_nodes;
    size_t node_counter = 0;
    
    // Process nodes in breadth-first order
    while (!node_queue.empty()) {
        TreeNode current_node = node_queue.front();
        node_queue.pop();
        
        std::string node_id = "node_" + std::to_string(node_counter++);
        processTreeNode(current_node, node_id, node_counter, tree_nodes, node_queue);
    }
    
    return tree_nodes;
}

// Process a single tree node
void GeoPointSorter::processTreeNode(
    TreeNode& current_node, 
    const std::string& node_id, 
    size_t& node_counter,
    std::map<std::string, TreeNode>& tree_nodes, 
    std::queue<TreeNode>& node_queue) {
    
    size_t node_points = current_node.stop - current_node.start;
    
    std::cout << "Processing " << node_id << ": points " 
              << current_node.start << " to " << current_node.stop
              << " (" << node_points << " points, "
              << (node_points * sizeof(Point) / (1024.0 * 1024.0)) << " MB)" << std::endl;
    
    // If partition is small enough, make it a leaf node
    if (node_points <= min_partition_points_) {
        std::cout << "  Leaf node created (below minimum size)" << std::endl;
        tree_nodes[node_id] = current_node;
        return;
    }
    
    // Sort and split the node
    splitTreeNode(current_node, node_id, node_counter, tree_nodes, node_queue);
}

// Sort and split a tree node
void GeoPointSorter::splitTreeNode(
    TreeNode& current_node, 
    const std::string& node_id, 
    size_t& node_counter,
    std::map<std::string, TreeNode>& tree_nodes, 
    std::queue<TreeNode>& node_queue) {
    
    size_t node_points = current_node.stop - current_node.start;
    
    // Sort this partition by the current dimension
    std::cout << "  Sorting partition by " << (current_node.xy_flag ? "X" : "Y") << std::endl;
    sortOnDisk(current_node.xy_flag, current_node.start, current_node.stop);
    
    // Find the median point
    Point median_point;
    size_t median_idx = findMedianPoint(current_node, median_point);
    
    // Get the delimiter value based on the current dimension
    double delimiter = current_node.xy_flag ? median_point.x : median_point.y;
    std::cout << "  Median at index " << median_idx << ", value: " << delimiter << std::endl;
    
    // Create child nodes
    createChildNodes(current_node, node_id, median_idx, delimiter, node_counter, tree_nodes, node_queue);
}

// Find the median point in a sorted partition
size_t GeoPointSorter::findMedianPoint(const TreeNode& node, Point& median_point) {
    size_t node_points = node.stop - node.start;
    size_t median_idx = node.start + (node_points / 2);
    
    // Create a temporary buffer to read a small section around the median
    const size_t BUFFER_SIZE = 3; // Read 3 points: median-1, median, median+1
    size_t buffer_start = median_idx > 0 ? median_idx - 1 : median_idx;
    size_t buffer_size = std::min(BUFFER_SIZE, node.stop - buffer_start);
    
    std::cout << "  Reading median area: points " << buffer_start << " to " 
              << (buffer_start + buffer_size) << std::endl;
    
    // Open the sorted output file
    std::ifstream sorted_file(sorted_output_path_, std::ios::binary);
    if (!sorted_file) {
        throw std::runtime_error("Could not open sorted file: " + sorted_output_path_);
    }
    
    // Read a small buffer around the median
    std::vector<Point> median_buffer(buffer_size);
    sorted_file.seekg(0); // Start from the beginning of the file
    
    // Read the entire buffer
    if (!sorted_file.read(reinterpret_cast<char*>(median_buffer.data()), 
                         buffer_size * sizeof(Point))) {
        throw std::runtime_error("Failed to read median area from sorted file");
    }
    
    // Get the median point (middle of the buffer)
    size_t median_buffer_idx = median_idx - buffer_start;
    if (median_buffer_idx >= median_buffer.size()) {
        throw std::runtime_error("Median index calculation error");
    }
    
    median_point = median_buffer[median_buffer_idx];
    return median_idx;
}

// Create child nodes for a split node
void GeoPointSorter::createChildNodes(
    TreeNode& current_node, 
    const std::string& node_id, 
    size_t median_idx, 
    double delimiter,
    size_t& node_counter,
    std::map<std::string, TreeNode>& tree_nodes, 
    std::queue<TreeNode>& node_queue) {
    
    // Create left child node
    TreeNode left_child;
    left_child.start = current_node.start;
    left_child.stop = median_idx;
    left_child.xy_flag = !current_node.xy_flag; // Alternate dimension
    
    // Create right child node
    TreeNode right_child;
    right_child.start = median_idx;
    right_child.stop = current_node.stop;
    right_child.xy_flag = !current_node.xy_flag; // Alternate dimension
    
    // Generate child node IDs
    std::string left_id = "node_" + std::to_string(node_counter++);
    std::string right_id = "node_" + std::to_string(node_counter++);
    
    // Update current node with split information
    current_node.split = median_idx;
    current_node.delim = delimiter;
    current_node.left_child = left_id;
    current_node.right_child = right_id;
    
    // Store the current node
    tree_nodes[node_id] = current_node;
    
    // Add child nodes to the queue
    node_queue.push(left_child);
    node_queue.push(right_child);
}

// Write the tree structure to a file in JSON format
void GeoPointSorter::writeTreeToFile(const std::map<std::string, TreeNode>& tree_nodes) {
    std::ofstream tree_file(config_.output_tree_path);
    if (!tree_file) {
        throw std::runtime_error("Could not open tree output file for writing: " + config_.output_tree_path);
    }
    
    // Write the tree to the output file in JSON format
    tree_file << "{\n";
    tree_file << "  \"root\": \"node_0\",\n";
    tree_file << "  \"nodes\": {\n";
    
    size_t node_index = 0;
    for (const auto& [id, node] : tree_nodes) {
        tree_file << "    \"" << id << "\": {\n";
        tree_file << "      \"start\": " << node.start << ",\n";
        tree_file << "      \"stop\": " << node.stop << ",\n";
        
        // Only internal nodes have these properties
        if (!node.left_child.empty()) {
            tree_file << "      \"split\": " << node.split << ",\n";
            tree_file << "      \"delim\": " << node.delim << ",\n";
            tree_file << "      \"dimension\": \"" << (node.xy_flag ? "x" : "y") << "\",\n";
            tree_file << "      \"left\": \"" << node.left_child << "\",\n";
            tree_file << "      \"right\": \"" << node.right_child << "\"\n";
        } else {
            tree_file << "      \"leaf\": true\n";
        }
        
        // Add comma if not the last node
        if (node_index < tree_nodes.size() - 1) {
            tree_file << "    },\n";
        } else {
            tree_file << "    }\n";
        }
        node_index++;
    }
    
    tree_file << "  }\n";
    tree_file << "}\n";
}

GeoPointSorter::~GeoPointSorter() = default; 