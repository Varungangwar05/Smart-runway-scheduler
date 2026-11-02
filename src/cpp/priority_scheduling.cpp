#include "flight.h"

#include <algorithm>
#include <stdexcept>
#include <vector>

namespace smart_runway {
namespace {

int effectivePriority(const Flight& flight, int agingIntervalMinutes) {
    if (flight.emergency) {
        return 1;
    }

    const int basePriority = std::max(1, flight.priorityLevel);
    const int waitingMinutes = std::max(0, flight.waitingMinutes);
    const int priorityImprovement = waitingMinutes / agingIntervalMinutes;

    return std::max(1, basePriority - priorityImprovement);
}

}  // namespace

// Pass only flights that are waiting for a runway.
// Returns them in scheduling order without changing the original list.
std::vector<Flight> scheduleByPriority(
    std::vector<Flight> flights,
    int agingIntervalMinutes
) {
    if (agingIntervalMinutes <= 0) {
        throw std::invalid_argument(
            "Aging interval must be greater than zero."
        );
    }

    std::stable_sort(
        flights.begin(),
        flights.end(),
        [agingIntervalMinutes](const Flight& first, const Flight& second) {
            // Emergency flights always come first.
            if (first.emergency != second.emergency) {
                return first.emergency;
            }

            const int firstPriority =
                effectivePriority(first, agingIntervalMinutes);
            const int secondPriority =
                effectivePriority(second, agingIntervalMinutes);

            // Lower number means higher priority.
            if (firstPriority != secondPriority) {
                return firstPriority < secondPriority;
            }

            // Break ties using arrival order, then scheduled time.
            if (first.requestOrder != second.requestOrder) {
                return first.requestOrder < second.requestOrder;
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