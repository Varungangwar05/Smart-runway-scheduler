#include "synchronization.h"
#include "priority_scheduling.h"

#include <stdexcept>
#include <utility>

namespace smart_runway {

void SynchronizedFlightQueue::submit(Flight flight) {
    {
        std::lock_guard<std::mutex> lock(mutex_);

        if (stopped_) {
            throw std::logic_error(
                "Cannot submit a flight after the queue has stopped."
            );
        }

        waitingFlights_.push_back(std::move(flight));
    }

    condition_.notify_one();
}

std::optional<Flight> SynchronizedFlightQueue::tryTakeNext() {
    std::lock_guard<std::mutex> lock(mutex_);
    return takeNextLocked();
}

std::optional<Flight> SynchronizedFlightQueue::waitAndTakeNext() {
    std::unique_lock<std::mutex> lock(mutex_);

    condition_.wait(lock, [this] {
        return stopped_ || !waitingFlights_.empty();
    });

    return takeNextLocked();
}

void SynchronizedFlightQueue::stop() {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        stopped_ = true;
    }

    condition_.notify_all();
}

// Call this only while mutex_ is locked.
std::optional<Flight> SynchronizedFlightQueue::takeNextLocked() {
    if (waitingFlights_.empty()) {
        return std::nullopt;
    }

    const std::vector<Flight> orderedFlights =
        scheduleByPriority(waitingFlights_, 10);

    const Flight nextFlight = orderedFlights.front();

    waitingFlights_.assign(
        orderedFlights.begin() + 1,
        orderedFlights.end()
    );

    return nextFlight;
}

}  // namespace smart_runway