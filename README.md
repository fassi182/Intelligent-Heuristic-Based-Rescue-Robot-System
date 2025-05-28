# Intelligent Heuristic-Based Rescue Robot System

## Project Description
This project implements a GUI-based rescue robot simulation that uses the A* algorithm with Manhattan distance to navigate a grid, prioritize victims by criticality, and perform rescues. The system features interactive visualization with step-by-step controls.

## Key Features
- **A\*** Pathfinding – Efficient obstacle avoidance and optimal routing  
- **Victim Prioritization** – Highest criticality first, then proximity  
- **Interactive GUI** – Visualizes robot movement, victims (color-coded by severity), and obstacles  
- **Treatment Modes** – On-site treatment or hospital transport  
- **Simulation Controls** – Start, Next Step, and Reset functionality  

## Limitations
- Fixed environment (no dynamic updates)  
- Basic treatment logic (binary on-site/hospital decision)  
- No error handling for edge cases  
- Manual step-by-step execution (no auto-play)  

## How It Works
- **Initialization** – Loads a predefined grid with victims, obstacles, and a hospital.  
- **Victim Selection** – Chooses the most critical victim first.  
- **Pathfinding** – Uses A* to navigate to the victim.  
- **Rescue Decision** – Treats on-site or transports to the hospital.  
- **Completion** – Returns to start after all rescues.  

## Future Improvements
- Dynamic map editing  
- Real-time algorithm visualization  
- Multi-robot coordination  
- Enhanced treatment options  
