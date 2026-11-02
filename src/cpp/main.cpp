#include "fcfs.h"
#include "priority_scheduling.h"

#include <iostream>
#include <string>
#include <vector>

namespace {

std::string operationName(FlightOperation operation) {
    if (operation == FlightOperation::Landing) {
        return "LANDING";
    }

    return "TAKEOFF";
}

}  // namespace

int main() {
    using namespace smart_runway;

    int algorithmChoice = 0;

    std::cout << "=== Smart Runway Scheduler ===\n";
    std::cout << "1. First-Come, First-Served (FCFS)\n";
    std::cout << "2. Priority Scheduling\n";
    std::cout << "Choose scheduling method: ";

    if (!(std::cin >> algorithmChoice)
        || (algorithmChoice != 1 && algorithmChoice != 2)) {
        std::cerr << "Please choose 1 or 2.\n";
        return 1;
    }

    int flightCount = 0;
    std::cout << "Number of flights to schedule (1-50): ";

    if (!(std::cin >> flightCount) || flightCount < 1 || flightCount > 50) {
        std::cerr << "Enter a number between 1 and 50.\n";
        return 1;
    }

    std::vector<Flight> flights;

    for (int index = 0; index < flightCount; ++index) {
        Flight flight{};
        int operationChoice = 0;
        int emergencyChoice = 0;

        flight.flightId = index + 1;
        flight.requestOrder = index + 1;
        flight.status = FlightStatus::Waiting;

        std::cout << "\nFlight " << index + 1 << "\n";
        std::cout << "Flight number (example: DA101): ";

        if (!(std::cin >> flight.flightNumber)) {
            std::cerr << "Invalid flight number.\n";
            return 1;
        }

        std::cout << "Operation (1 = Landing, 2 = Takeoff): ";
        if (!(std::cin >> operationChoice)
            || (operationChoice != 1 && operationChoice != 2)) {
            std::cerr << "Enter 1 for Landing or 2 for Takeoff.\n";
            return 1;
        }

        flight.operation = (operationChoice == 1)
            ? FlightOperation::Landing
            : FlightOperation::Takeoff;

        std::cout << "Priority (1 = highest, 5 = lowest): ";
        if (!(std::cin >> flight.priorityLevel)
            || flight.priorityLevel < 1
            || flight.priorityLevel > 5) {
            std::cerr << "Enter a priority between 1 and 5.\n";
            return 1;
        }

        std::cout << "Emergency? (1 = Yes, 0 = No): ";
        if (!(std::cin >> emergencyChoice)
            || (emergencyChoice != 0 && emergencyChoice != 1)) {
            std::cerr << "Enter 1 for Yes or 0 for No.\n";
            return 1;
        }

        flight.emergency = (emergencyChoice == 1);

        std::cout << "Waiting time in minutes: ";
        if (!(std::cin >> flight.waitingMinutes)
            || flight.waitingMinutes < 0) {
            std::cerr << "Waiting time cannot be negative.\n";
            return 1;
        }

        flights.push_back(flight);
    }

    const std::vector<Flight> scheduledFlights =
        (algorithmChoice == 1)
            ? scheduleFCFS(flights)
            : scheduleByPriority(flights);

    std::cout << "\n=== Scheduling Order ===\n";

    for (std::size_t index = 0; index < scheduledFlights.size(); ++index) {
        const Flight& flight = scheduledFlights[index];

        std::cout << index + 1 << ". "
                  << flight.flightNumber << " | "
                  << operationName(flight.operation) << " | Priority "
                  << flight.priorityLevel;

        if (flight.emergency) {
            std::cout << " | EMERGENCY";
        }

        std::cout << '\n';
    }

    return 0;
}