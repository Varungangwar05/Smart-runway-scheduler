#pragma once

#include "flight.h"

#include <vector>

namespace smart_runway {

std::vector<Flight> scheduleByPriority(
    std::vector<Flight> flights,
    int agingIntervalMinutes = 10
);

}  // namespace smart_runway