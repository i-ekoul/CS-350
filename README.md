# CS-350 — Emerging Systems Architectures and Technologies

**Author:** Emmalie S. Cole  
**Course:** CS350 – Emerging Systems Architectures and Technologies  
**Institution:** Southern New Hampshire University  

This repository contains selected portfolio artifacts from CS350 that demonstrate my ability to design, implement, and analyze embedded and emerging systems architectures. The work highlights direct hardware–software interaction, serial communication, system-level design decisions, and architectural tradeoff analysis.

---

## Portfolio Artifacts Overview

This repository includes **two primary artifacts** selected to best represent my technical strengths and learning outcomes in this course.

---

## Artifact One: UART-Based Client–Server Hardware Control System

**Location:** `Artifact-1/`

This artifact is a multi-file Python project implementing a **client–server architecture over UART** to control hardware on a Raspberry Pi. A serial client sends ASCII commands over a USB-to-TTL connection, which are received by a UART server running on the Pi. The server validates commands, controls GPIO output to actuate an LED, sends acknowledgments, and performs safe cleanup on shutdown.

### Key Capabilities Demonstrated
- Serial communication using UART
- Hardware control via GPIO
- Client–server message handling
- Structured command parsing and validation
- Fault tolerance and graceful shutdown
- Hardware-safe cleanup and resource management

### Technologies Used
- Python 3
- Raspberry Pi
- UART (`pySerial`)
- GPIO (`RPi.GPIO`)
- USB-to-TTL serial communication

This artifact demonstrates my ability to write **interface software that directly controls hardware components** while accounting for system constraints and reliability.

---

## Artifact Two: Smart Thermostat System — Architecture & Design Analysis

**Location:** `Artifact-2/`

This artifact represents a complete **embedded systems prototype and architectural evaluation** centered around a smart thermostat implemented on a Raspberry Pi. The system integrates sensors, actuators, user input, display output, and telemetry, supported by a documented state machine and a production-oriented architecture analysis.

### Prototype Features
- Temperature and humidity sensing via I²C
- User input via multiple GPIO buttons with debounce
- PWM-controlled LEDs for heating/cooling indication
- LCD output using a 16×2 HD44780 display
- UART telemetry output at fixed intervals
- Event-driven finite state machine (OFF / HEAT / COOL)

### Architecture Analysis
The accompanying report evaluates multiple **production-ready hardware architectures**, including:
- Raspberry Pi (Linux SBC)
- Microchip PIC32MZ-W1 (WFI32E01 Wi-Fi MCU module)
- NXP i.MX RT crossover MCU with external Wi-Fi

Each option is compared based on:
- Peripheral support (GPIO, PWM, I²C, UART)
- Memory and performance constraints
- Power consumption
- Certification and scalability considerations

A justified recommendation is provided for transitioning the prototype to a production-grade embedded platform.

### Skills Demonstrated
- Hardware architecture evaluation
- Embedded system design under constraints
- State machine modeling
- Interface selection and justification
- Maintainable and extensible embedded software design

This artifact demonstrates my ability to **analyze and recommend emerging systems architectures based on functional and business requirements**.

---

## Reflection on Learning

### What I Did Well
I consistently applied a structured, methodical approach to embedded problem solving. I focused on isolating variables, validating assumptions, and testing incrementally, which proved especially effective when debugging hardware–software interactions. I also emphasized clarity and documentation to ensure my work remained understandable and maintainable.

### Areas for Improvement
I would benefit from incorporating more advanced diagnostic tooling earlier in the development process to reduce troubleshooting time. As I continue working with embedded systems, I aim to improve efficiency by refining initial design assumptions and expanding my use of debugging and monitoring techniques.

### Tools and Resources Added
- Official hardware documentation and datasheets
- Structured use of GitHub for version control and portfolio organization
- Serial debugging and monitoring workflows
- State machine diagrams for system reasoning

### Transferable Skills
The skills developed in this course are highly transferable to future coursework and professional roles, including:
- Embedded debugging and system isolation
- Hardware–software integration
- Architectural tradeoff analysis
- Writing maintainable, readable, and adaptable code

### Maintainability and Adaptability
I emphasized clear naming conventions, modular design, and consistent formatting throughout all code artifacts. Hardware assumptions and configuration decisions are documented to support future modification or platform migration with minimal refactoring.

## Repository Structure

