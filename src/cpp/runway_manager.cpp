#include "runway_manager.h"

namespace smart_runway {
namespace {

bool hasTimeConflict(
    const std::vector<TimeWindow>& windows,
    const std::string& operationStartTime,
    const std::string& operationEndTime
) {
    for (const TimeWindow& window : windows) {
        // Invalid window data blocks the runway.
        if (window.startTime.empty()
            || window.endTime.empty()
            || window.startTime >= window.endTime) {
            return true;
        }

        // Both time ranges use YYYY-MM-DD HH:MM:SS format.
        const bool overlaps =
            operationStartTime < window.endTime
            && window.startTime < operationEndTime;

        if (overlaps) {
            return true;
        }
    }

    return false;
}

}  // namespace

bool isRunwayAvailable(
    const Runway& runway,
    const Flight& flight,
    const std::string& operationStartTime,
    const std::string& operationEndTime
) {
    if (!runway.isActive
        || operationStartTime.empty()
        || operationEndTime.empty()
        || operationStartTime >= operationEndTime) {
        return false;
    }

    if (flight.operation == FlightOperation::Landing
        && !runway.supportsLandings) {
        return false;
    }

    if (flight.operation == FlightOperation::Takeoff
        && !runway.supportsTakeoffs) {
        return false;
    }

    if (hasTimeConflict(
            runway.maintenanceWindows,
            operationStartTime,
            operationEndTime)) {
        return false;
    }

    if (hasTimeConflict(
            runway.allocatedWindows,
            operationStartTime,
            operationEndTime)) {
        return false;
    }

    return true;
}

}  // namespace smart_runway