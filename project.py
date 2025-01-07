import random
import heapq
import time

class Server:
    def __init__(self, id, max_load=5, latency=10):
        self.id = id
        self.current_load = 0  
        self.max_load = max_load
        self.latency = latency
        self.active = True

    def add_request(self):
        if self.current_load < self.max_load:
            self.current_load += 1
            return True
        return False

    def remove_request(self):
        if self.current_load > 0:
            self.current_load -= 1

    def is_overloaded(self):
        return self.current_load >= self.max_load

    def set_active(self, status):
        self.active = status

class DLNode:
    def __init__(self, server):
        self.server = server
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, server):
        new_node = DLNode(server)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.size += 1

    def remove(self, node):
        if node == self.head:
            self.head = node.next
        if node == self.tail:
            self.tail = node.prev
        if node.prev:
            node.prev.next = node.next  
        if node.next:
            node.next.prev = node.prev
        self.size -= 1

class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, server):
        heapq.heappush(self.heap, (server.current_load, server.id, server))

    def pop(self):
        return heapq.heappop(self.heap)[2]

    def update(self):
        heapq.heapify(self.heap)

class ClientSessionAVLNode:
    def __init__(self, session_id, server):
        self.session_id = session_id
        self.server = server
        self.left = None
        self.right = None
        self.height = 1  # Height of the node for balancing

class ClientSessionAVL:
    def __init__(self):
        self.root = None

    def insert(self, session_id, server):
        self.root = self._insert_recursive(self.root, session_id, server)

    def _insert_recursive(self, node, session_id, server):
        if not node:
            return ClientSessionAVLNode(session_id, server)
        
        if session_id < node.session_id:
            node.left = self._insert_recursive(node.left, session_id, server)
        elif session_id > node.session_id:
            node.right = self._insert_recursive(node.right, session_id, server)
        else:
            node.server = server  # Update server if session ID already exists
            return node

        # Update the height of this node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # Balance the node
        balance_factor = self._get_balance(node)

        # Left Left Case
        if balance_factor > 1 and session_id < node.left.session_id:
            return self._right_rotate(node)

        # Right Right Case
        if balance_factor < -1 and session_id > node.right.session_id:
            return self._left_rotate(node)

        # Left Right Case
        if balance_factor > 1 and session_id > node.left.session_id:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Right Left Case
        if balance_factor < -1 and session_id < node.right.session_id:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def search(self, session_id):
        return self._search_recursive(self.root, session_id)

    def _search_recursive(self, node, session_id):
        if not node:
            return None
        if session_id == node.session_id:
            return node.server
        elif session_id < node.session_id:
            return self._search_recursive(node.left, session_id)
        else:
            return self._search_recursive(node.right, session_id)

    def _left_rotate(self, z):
        y = z.right
        T2 = y.left

        # Perform rotation
        y.left = z
        z.right = T2

        # Update heights
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _right_rotate(self, z):
        y = z.left
        T3 = y.right

        # Perform rotation
        y.right = z
        z.left = T3

        # Update heights
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _get_height(self, node):
        if not node:
            return 0
        return node.height

    def _get_balance(self, node):
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

class Graph:
    def __init__(self):
        self.adjacency_list = {}

    def add_edge(self, server_a, server_b, weight):
        if server_a.id not in self.adjacency_list:
            self.adjacency_list[server_a.id] = []
        if server_b.id not in self.adjacency_list:
            self.adjacency_list[server_b.id] = []
        self.adjacency_list[server_a.id].append((server_b.id, weight))
        self.adjacency_list[server_b.id].append((server_a.id, weight))

    def get_neighbors(self, server_id):
        return self.adjacency_list.get(server_id, [])

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.round_robin_list = DoublyLinkedList()
        self.session_avl = ClientSessionAVL()
        self.heap = MinHeap()
        self.graph = Graph()
        self.logs = []
        self.current_rr_node = None

        for i, server in enumerate(servers):
            self.round_robin_list.append(server)
            self.heap.push(server)
            for j in range(i + 1, len(servers)):
                self.graph.add_edge(server, servers[j], servers[j].latency)

    def get_least_loaded_server(self):
        return self.heap.pop()

    def get_next_server_round_robin(self):
        if not self.current_rr_node:
            self.current_rr_node = self.round_robin_list.head
        else:
            self.current_rr_node = self.current_rr_node.next if self.current_rr_node.next else self.round_robin_list.head
        return self.current_rr_node.server

    def get_server_by_session(self, session_id):
        server = self.session_avl.search(session_id)
        if server:
            return server
        else:
            server = self.get_least_loaded_server()
            self.session_avl.insert(session_id, server)
            return server
    
    def get_low_latency_server(self, server_id):
        neighbors = self.graph.get_neighbors(server_id)
        min_latency_server = None
        min_latency = float('inf')

        for neighbor_id, latency in neighbors:
            neighbor_server = next((s for s in self.servers if s.id == neighbor_id), None)
            if neighbor_server and not neighbor_server.is_overloaded() and latency < min_latency:
                min_latency = latency
                min_latency_server = neighbor_server

        return min_latency_server if min_latency_server else self.get_least_loaded_server()

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        self.logs.append(f"[{timestamp}] {message}")
        print(self.logs[-1])

    def scale_up(self, new_servers):
        for server in new_servers:
            self.servers.append(server)
            self.round_robin_list.append(server)
            self.heap.push(server)
            self.log(f"Server {server.id} added to load balancer.")

    def scale_down(self, server_ids_to_remove):
        for server in self.servers[:]:
            if server.id in server_ids_to_remove:
                self.servers.remove(server)
                self.log(f"Server {server.id} removed from load balancer.")
                node = self.round_robin_list.head
                while node:
                    if node.server.id == server.id:
                        self.round_robin_list.remove(node)
                        break
                    node = node.next
                self.heap.update()

    def simulate_server_failure(self, server_id):
        for server in self.servers:
            if server.id == server_id:
                server.set_active(False)
                self.log(f"Server {server.id} is down.")

    def recover_server(self, server_id):
        for server in self.servers:
            if server.id == server_id:
                server.set_active(True)
                self.log(f"Server {server.id} is back online.")

    def add_request(self, session_id=None, method='least'):
        if method == 'least':
            server = self.get_least_loaded_server()
        elif method == 'round_robin':
            server = self.get_next_server_round_robin()
        elif method == 'hash':
            server = self.get_server_by_session(session_id)
        elif method == 'latency':
            starting_server = random.choice(self.servers)
            server = self.get_low_latency_server(starting_server.id)

        if server.add_request():
            self.log(f"Request assigned to Server {server.id}. Current load: {server.current_load}/{server.max_load}")
        else:
            self.log(f"Server {server.id} is overloaded. Request could not be assigned.")
        self.heap.push(server)

    def remove_request(self, server_id):
        for server in self.servers:
            if server.id == server_id:
                if server.current_load == 0:
                    print("Server has no requests to remove")
                else:
                    server.remove_request()
                    self.log(f"Request removed from Server {server.id}. Current load: {server.current_load}/{server.max_load}")
                    self.heap.update()
                break





# Initialize servers and load balancer
servers = [Server(id=i, max_load=5, latency=random.randint(5, 20)) for i in range(1, 4)]
load_balancer = LoadBalancer(servers)

def display_menu():
    print("\nMenu:")
    print("1. Add Request")
    print("2. Remove Request")
    print("3. Scale Up (Add New Servers)")
    print("4. Scale Down (Remove Servers)")
    print("5. Simulate Server Failure")
    print("6. Recover Server")
    print("7. View Logs")
    print("8. Exit")

def menu():
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            session_id = input("Enter session ID (e.g., client_1): ")
            method = input("Enter load balancing method (least, round_robin, hash,latency): ").lower()
            load_balancer.add_request(session_id=session_id, method=method)

        elif choice == '2':
            server_id = int(input("Enter server ID to remove request from: "))
            load_balancer.remove_request(server_id)

        elif choice == '3':
            num_new_servers = int(input("Enter number of new servers to add: "))
            new_servers = [Server(id=len(servers) + i + 1, max_load=5, latency=random.randint(5, 20)) for i in range(num_new_servers)]
            load_balancer.scale_up(new_servers)

        elif choice == '4':
            server_ids_to_remove = input("Enter server IDs to remove (comma-separated): ").split(',')
            server_ids_to_remove = [int(id.strip()) for id in server_ids_to_remove]
            load_balancer.scale_down(server_ids_to_remove)

        elif choice == '5':
            server_id = int(input("Enter server ID to simulate failure: "))
            load_balancer.simulate_server_failure(server_id)

        elif choice == '6':
            server_id = int(input("Enter server ID to recover: "))
            load_balancer.recover_server(server_id)

        elif choice == '7':
            print("\nLogs:")
            for log in load_balancer.logs:
                print(log)

        elif choice == '8':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please select a valid option.")

# Run the menu
menu()
