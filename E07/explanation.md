# Theoretical background

## Lab map
The lab starts from the TCP/IP model and moves down to practical details about routing, subnets, transport protocols, and application services.

## Core concepts

### Routing and routing tables
A router decides where to forward packets by looking at the destination and consulting its routing table.

### Subnet
A subnet divides a larger network into smaller blocks to organize addresses and broadcast domains.

### Switch and router
- A switch works locally and forwards frames inside the LAN.
- A router connects different networks and decides the paths toward other subnets or the Internet.

### Unicast, broadcast, multicast, anycast
- `Unicast`: one sender, one recipient.
- `Broadcast`: one sender, all nodes in the local network.
- `Multicast`: one sender, a group.
- `Anycast`: one sender, the nearest recipient among several candidates.

### Reliable data transfer
The reliable data transfer part explains concepts such as ACKs, retransmission, sliding windows, and error control.

### BGP and RIP
- RIP is simpler and older, based on hop count as its metric.
- BGP is the protocol used between autonomous systems on the Internet.

### HTTP, REST, and TLS
HTTP defines how requests and responses travel; REST uses HTTP to expose resources; TLS adds encryption and integrity.
