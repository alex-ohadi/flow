cmake_minimum_required(VERSION 3.14)
project(hmm_map_matcher)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories - add path for Python, pybind11, and nlohmann-json
include_directories(
    /usr/include/python3.9  # Assuming Python 3.9 is used, adjust if different
    third_party/nlohmann-json  # Include manually downloaded nlohmann-json header (if needed)
)

# Find Python and pybind11
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

# Tell CMake where to find pybind11
list(APPEND CMAKE_PREFIX_PATH "/usr/local/include/pybind11")

# Find pybind11
find_package(pybind11 REQUIRED)

# Add the C++ module and link it with pybind11
add_library(hmm_map_matcher MODULE mapmatcher.cpp)
target_link_libraries(hmm_map_matcher PRIVATE pybind11::module)

# If you installed nlohmann-json via package manager, link it like this:
find_package(nlohmann_json REQUIRED)
target_link_libraries(hmm_map_matcher PRIVATE nlohmann_json::nlohmann_json)
