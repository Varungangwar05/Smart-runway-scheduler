#pragma once

#include "flight.h"

#include <condition_variable>
#include <mutex>
#include <optional>
#include <vector>

namespace smart_runway {

class SynchronizedFlightQueue {
public:
    void submit(Flight flight);

    // Returns no flight if the queue is empty.
    std::optional<Flight> tryTakeNext();

    // Waits for a flight, or returns no flight after stop().
    std::optional<Flight> waitAndTakeNext();

    // Wakes waiting threads and prevents new submissions.
    void stop();

private:
    std::optional<Flight> takeNextLocked();

    std::mutex mutex_;
    std::condition_variable condition_;
    std::vector<Flight> waitingFlights_;
    bool stopped_{false};
};

}  // namespace smart_runway