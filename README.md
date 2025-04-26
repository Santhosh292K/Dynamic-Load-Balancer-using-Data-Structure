# 🧠 Intelligent Load Balancer Simulation

This Python-based simulation models a **multi-server load balancer** that distributes incoming client requests using multiple advanced data structures and load balancing strategies. The project supports real-time scaling, server failure recovery, and request handling through a menu-driven interface.

## 🚀 Features

- **Load Balancing Strategies:**
  - 🧮 Least Load (MinHeap)
  - 🔁 Round Robin (Doubly Linked List)
  - 🔐 Consistent Hashing (AVL Tree)
  - ⚡ Latency-Aware Routing (Graph)

- **Dynamic Scaling:**
  - Scale up by adding new servers
  - Scale down by removing specified servers

- **Server State Simulation:**
  - Simulate server failure
  - Recover failed servers

- **Real-time Logging:**
  - View detailed logs with timestamps for request assignments and server status updates

## 🧱 Data Structures Used

- `MinHeap`: Efficiently selects the least loaded server
- `DoublyLinkedList`: Implements round-robin traversal
- `AVL Tree`: Maintains session-to-server mapping for hash-based routing
- `Graph`: Models server-to-server latency for latency-aware decisions

## 📦 Requirements

- Python 3.x

> No external libraries are required—everything runs on Python’s standard library.

## 📂 How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/load-balancer-simulator.git
   cd load-balancer-simulator
2.Run the simulation:
      python load_balancer_simulation.py
3.Use the terminal-based menu to interact:
      Menu:
      1. Add Request
      2. Remove Request
      3. Scale Up (Add New Servers)
      4. Scale Down (Remove Servers)
      5. Simulate Server Failure
      6. Recover Server
      7. View Logs
      8. Exit


