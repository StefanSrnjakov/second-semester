CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra
INCLUDES = -I./include

# Output binary
TARGET = geo_point_sorter

# Source files
SRCS = main.cpp geo_point_sorter.cpp file_handler.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(OBJS) -o $(TARGET)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean 