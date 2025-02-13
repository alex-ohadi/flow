#include <iostream>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <fstream>
#include <nlohmann/json.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using json = nlohmann::json;

struct GPSPoint {
    double latitude;
    double longitude;
};

struct RoadSegment {
    std::string id;
    std::vector<GPSPoint> coordinates;
};

class HMMMapMatcher {
public:
    HMMMapMatcher(const std::vector<RoadSegment>& roadNetwork) : roadNetwork(roadNetwork) {}
    
    std::vector<std::string> matchTraceToRoads(const std::vector<GPSPoint>& gpsTrace) {
        std::vector<std::string> matchedSegments;
        for (const auto& gps : gpsTrace) {
            std::string closestSegment = findClosestRoadSegment(gps);
            matchedSegments.push_back(closestSegment);
        }
        return matchedSegments;
    }

private:
    std::vector<RoadSegment> roadNetwork;
    
    double haversineDistance(const GPSPoint& a, const GPSPoint& b) {
        constexpr double R = 6371e3; // Earth radius in meters
        double lat1 = a.latitude * M_PI / 180.0;
        double lat2 = b.latitude * M_PI / 180.0;
        double dLat = (b.latitude - a.latitude) * M_PI / 180.0;
        double dLon = (b.longitude - a.longitude) * M_PI / 180.0;
        
        double a_h = sin(dLat/2) * sin(dLat/2) +
                     cos(lat1) * cos(lat2) *
                     sin(dLon/2) * sin(dLon/2);
        double c = 2 * atan2(sqrt(a_h), sqrt(1-a_h));
        return R * c;
    }
    
    std::string findClosestRoadSegment(const GPSPoint& gps) {
        std::string closestId = "";
        double minDistance = std::numeric_limits<double>::max();
        
        for (const auto& segment : roadNetwork) {
            for (const auto& point : segment.coordinates) {
                double dist = haversineDistance(gps, point);
                if (dist < minDistance) {
                    minDistance = dist;
                    closestId = segment.id;
                }
            }
        }
        return closestId;
    }
};

// Helper functions to load data from JSON files
std::vector<RoadSegment> loadRoadNetwork(const std::string& filename) {
    std::ifstream file(filename);
    json data;
    file >> data;
    
    std::vector<RoadSegment> roadNetwork;
    std::cout << "Loading Road Network from: " << filename << std::endl;

    for (const auto& edge : data) {
        RoadSegment segment;
        segment.id = edge["id"];
        std::cout << "  Loading segment with ID: " << segment.id << std::endl;
        for (const auto& coord : edge["gps"]["coordinates"]) {
            segment.coordinates.push_back({coord[1], coord[0]});
        }
        roadNetwork.push_back(segment);
    }
    std::cout << "Loaded " << roadNetwork.size() << " road segments." << std::endl;
    return roadNetwork;
}

std::vector<GPSPoint> loadGPSTrace(const std::string& filename) {
    std::ifstream file(filename);
    json data;
    file >> data;
    
    std::vector<GPSPoint> gpsTrace;
    std::cout << "Loading GPS Trace from: " << filename << std::endl;

    for (const auto& event : data) {
        gpsTrace.push_back({event["lat"], event["lon"]});
    }
    std::cout << "Loaded " << gpsTrace.size() << " GPS points." << std::endl;
    return gpsTrace;
}

std::vector<std::string> match_gps_to_roads(const std::string& edges_file, const std::string& events_file) {
    std::vector<RoadSegment> roadNetwork = loadRoadNetwork(edges_file);
    std::vector<GPSPoint> gpsTrace = loadGPSTrace(events_file);
    
    HMMMapMatcher matcher(roadNetwork);
    return matcher.matchTraceToRoads(gpsTrace);
}

// PYBIND11_MODULE to expose C++ classes and functions to Python
PYBIND11_MODULE(hmm_map_matcher, m) {
    // Expose GPSPoint class to Python
    py::class_<GPSPoint>(m, "GPSPoint")
        .def(py::init<>())
        .def_readwrite("latitude", &GPSPoint::latitude)
        .def_readwrite("longitude", &GPSPoint::longitude);

    // Expose RoadSegment class to Python
    py::class_<RoadSegment>(m, "RoadSegment")
        .def(py::init<>())
        .def_readwrite("id", &RoadSegment::id)
        .def_readwrite("coordinates", &RoadSegment::coordinates);

    // Expose HMMMapMatcher class to Python
    py::class_<HMMMapMatcher>(m, "HMMMapMatcher")
        .def(py::init<const std::vector<RoadSegment>&>())
        .def("matchTraceToRoads", &HMMMapMatcher::matchTraceToRoads);

    // Expose the function that matches GPS trace to roads
    m.def("match_gps_to_roads", &match_gps_to_roads, "Match GPS traces to road segments", 
          py::arg("edges_file"), py::arg("events_file"));
}
