#pragma once

#include "flight.h"

#include <vector>

namespace smart_runway {

std::vector<Flight> scheduleFCFS(std::vector<Flight> flights);

}  // namespace smart_runway