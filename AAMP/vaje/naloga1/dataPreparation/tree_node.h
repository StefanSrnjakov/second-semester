#pragma once

#include <string>
#include <cstddef>

class TreeNode {
public:
    // Constructors
    TreeNode() = default;
    TreeNode(size_t start, size_t stop, bool xy_flag);

    // Getters
    std::string getId() const { return id_; }
    size_t getStart() const { return start_; }
    size_t getStop() const { return stop_; }
    size_t getSplit() const { return split_; }
    double getDelim() const { return delim_; }
    bool getXyFlag() const { return xy_flag_; }
    std::string getLeftChild() const { return left_child_; }
    std::string getRightChild() const { return right_child_; }
    float getMinX() const { return min_x_; }
    float getMaxX() const { return max_x_; }
    float getMinY() const { return min_y_; }
    float getMaxY() const { return max_y_; }
    const std::string& getParent() const { return parent_; }

    // Setters
    void setId(const std::string& id) { id_ = id; }
    void setStart(size_t start) { start_ = start; }
    void setStop(size_t stop) { stop_ = stop; }
    void setSplit(size_t split) { split_ = split; }
    void setDelim(double delim) { delim_ = delim; }
    void setXyFlag(bool xy_flag) { xy_flag_ = xy_flag; }
    void setLeftChild(const std::string& left_child) { left_child_ = left_child; }
    void setRightChild(const std::string& right_child) { right_child_ = right_child; }
    void setMinX(float min_x) { min_x_ = min_x; }
    void setMaxX(float max_x) { max_x_ = max_x; }
    void setMinY(float min_y) { min_y_ = min_y; }
    void setMaxY(float max_y) { max_y_ = max_y; }
    void setParent(const std::string& parent) { parent_ = parent; }

private:
    std::string id_;
    size_t start_{0};
    size_t stop_{0};
    size_t split_{0};
    double delim_{0.0};
    bool xy_flag_{true};
    std::string left_child_;
    std::string right_child_;
    std::string parent_;
    float min_x_{0.0f};
    float max_x_{0.0f};
    float min_y_{0.0f};
    float max_y_{0.0f};
}; 