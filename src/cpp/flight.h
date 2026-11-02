#pragma once

#include <string>

enum class FlightOperation {
    Landing,
    Takeoff
};

enum class FlightStatus {
    Waiting,
    Scheduled,
    InProgress,
    Completed,
    Cancelled
};

struct Flight {
    int flightId{0};
    std::string flightNumber;
    int aircraftId{0};

    FlightOperation operation{FlightOperation::Landing};
    FlightStatus status{FlightStatus::Waiting};

    // Format: YYYY-MM-DD HH:MM:SS
    std::string scheduledTime;
    std::string requestedTime;

    // 1 is the highest priority.
    int priorityLevel{3};
    bool emergency{false};

    // Used for FCFS ordering and priority aging.
    int requestOrder{0};
    int waitingMinutes{0};
};