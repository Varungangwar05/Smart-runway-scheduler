#pragma once

#include "flight.h"

#include <string>
#include <vector>

namespace smart_runway {

struct TimeWindow {
    // Format: YYYY-MM-DD HH:MM:SS
    std::string startTime;
    std::string endTime;
};

struct Runway {
    int runwayId{0};
    std::string runwayCode;

    bool supportsLandings{true};
    bool supportsTakeoffs{true};
    bool isActive{true};

    std::vector<TimeWindow> maintenanceWindows;
    std::vector<TimeWindow> allocatedWindows;
};

bool isRunwayAvailable(
    const Runway& runway,
    const Flight& flight,
    const std::string& operationStartTime,
    const std::string& operationEndTime
);

}  // namespace smart_runway