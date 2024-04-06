# GatorGlide Delivery Co. Management System

The GatorGlide Delivery Co. Management System is a state-of-the-art software solution designed to optimize the logistics operations of delivery services. Utilizing advanced AVL trees, this system efficiently manages order priorities and delivery times, ensuring that the delivery process is both fast and reliable. Developed as part of the COP5536 - Advanced Data Structures course, this project showcases how data structures can be applied to solve real-world problems in innovative ways.

## Project Overview

This system aims to revolutionize the way delivery services operate by:
- Implementing AVL trees for dynamic order management based on priorities.
- Calculating order priorities using a balanced formula of order value and creation time.
- Scheduling deliveries efficiently by calculating and updating Estimated Time of Arrival (ETA) for each order.
- Operating under a model with a single delivery agent to optimize delivery routes and schedules.

## Getting Started

### Prerequisites

- Python 3.x

### Installation

1. Clone the repository to your local machine.
```git clone https://github.com/yourusername/gatorglide-delivery-system.git```

2. Navigate to the project directory.
```cd gatorglide-delivery-system```

3. Running the Program
- Place your input text file (e.g., test1.txt) in the project directory.
- Run the program using the following command:
```python gatorDelivery.py test1.txt```
- The output will be generated in a file named <input_file_name>_output_file.txt, detailing the order deliveries and system operations.

## Key Features

- AVL Tree for Order Management: Efficient access and modification operations for orders.
- Dynamic Priority Calculation: Fair and efficient order processing.
- Efficient Delivery Scheduling: Dynamic adjustments to ETAs based on new orders and cancellations.
- Single Delivery Agent Model: Optimized delivery route and schedule.
- Comprehensive System Operations: Supports creating, updating, and cancelling orders, along with advanced querying features.

## System Structure
- avl.py: Implements an AVL tree for order management.
- gatorDelivery.py: Main program file, handling input/output and system operations.
- order_management_system.py: Manages orders, calculates priorities, and updates ETAs.
- priority_queue.py: (Optional) Manages preprocessing of orders before AVL tree insertion.
