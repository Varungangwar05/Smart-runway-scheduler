# Smart Runway Scheduler

An academic project that demonstrates airport runway scheduling using C++17, Python, and MySQL.

## Features

- FCFS and Priority scheduling
- Emergency-flight priority and priority aging
- Flight queue and runway assignment
- Runway availability, maintenance, and allocation-overlap checks
- MySQL storage and recent activity history
- Mark an assigned flight as completed

## Technologies

- C++17
- Python with CustomTkinter
- MySQL

## Project structure

- `database/schema.sql` — database tables
- `database/seed.sql` — sample data
- `src/cpp/` — C++ scheduling modules
- `src/python/` — desktop dashboard and MySQL repositories

## Database setup

1. Start the MySQL server.
2. Open `database/schema.sql` in MySQL Workbench and run it.
3. Run `database/seed.sql`.

## Run the C++ console app

From the project folder in PowerShell:

```powershell
g++ -std=c++17 src/cpp/main.cpp src/cpp/fcfs.cpp src/cpp/priority_scheduling.cpp src/cpp/runway_manager.cpp src/cpp/synchronization.cpp -o smart_runway.exe
.\smart_runway.exe