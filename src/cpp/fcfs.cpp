#include "flight.h"

#include <algorithm>
#include <vector>

namespace smart_runway {

std::vector<Flight> scheduleFCFS(std::vector<Flight> flights) {
    std::stable_sort(
        flights.begin(),
        flights.end(),
        [](const Flight& first, const Flight& second) {
            // Emergency flights go first.
            if (first.emergency != second.emergency) {
                return first.emergency;
            }

            // Lower requestOrder means the flight arrived earlier.
            if (first.requestOrder != second.requestOrder) {
                return first.requestOrder < second.requestOrder;
            }

            // Use timestamps to break ties.
            if (first.requestedTime != second.requestedTime) {
                return first.requestedTime < second.requestedTime;
            }

            if (first.scheduledTime != second.scheduledTime) {
                return first.scheduledTime < second.scheduledTime;
            }

            return first.flightNumber < second.flightNumber;
        }
    );

    return flights;
}

}  // namespace smart_runway
