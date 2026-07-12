# Lab 07 Solutions: Network Protocols

This lab is theoretical/investigative: `solutions/questions.pdf`
(`E07_ Networking.pdf`) has five exercises built around Linux networking tools,
a live two-machine networking task, and conceptual questions about the OSI/
TCP/IP models, packet delivery, and NAT. There is no code to run; answers below
follow the exercises in order.

## Exercise 01: Examine the tools

**Task recap.** Document the purpose of `ip link`, `ip address`, `ip route`, and
`netstat`.

**Answers.**
1. **`ip link`** — shows and manages network interfaces (physical and virtual)
   at layer 2: their name, MAC address, MTU, and up/down state. `ip link show`
   lists all interfaces; `ip link set <iface> up|down` changes state.
2. **`ip address`** — shows and manages the IP addresses bound to each
   interface. `ip address show <iface>` lists the IPv4/IPv6 addresses on that
   interface; `ip address add <cidr> dev <iface>` assigns a new address.
3. **`ip route`** — shows and manages the kernel routing table: which
   interface/gateway to use for a given destination network. `ip route` lists
   current routes; `ip route add <network> via <gateway> dev <iface>` adds one.
4. **`netstat`** — shows current network connections and socket state (local
   and foreign address, protocol, connection state such as `ESTABLISHED`), and
   with flags like `-tuln` can also list listening TCP/UDP ports.

## Exercise 02: Take your own route

**Task recap.** Connect two (or more) computers directly, by switch, or by
hotspot; disable automatic IP assignment; manually assign IP addresses to each
machine's interface; add a route if needed; then have one machine reach the
other's Lab 02 Docker Compose site through the manually assigned IP.

**Answers (procedure).**
1. Disable DHCP/automatic addressing on the interface used for the direct link.
2. Assign a static address on each machine, e.g. `sudo ip address add
   192.168.10.2/24 dev eth0` on one machine and `192.168.10.3/24` on the other.
   Confirm with `ip address show eth0`.
3. If the two machines are not on a common broadcast domain (e.g. reaching a
   third subnet), add a route: `sudo ip route add 192.168.10.0/24 dev eth0`,
   confirmed with `ip route`.
4. Start the Lab 02 `docker compose` site on one machine.
5. From the other machine, browse to
   `http://<peer-static-ip>:8080` (the port published by the Lab 02 compose
   file) to confirm connectivity over the manually configured link.

This exercise has no artifact to keep in `materials/` — it requires two
physical machines on the same LAN segment and is inherently a live,
in-classroom exercise. It is documentation-verified only (see the "Validation"
note in the lab README).

## Exercise 03: Networking Models

**Task recap.** Discuss the OSI vs. TCP/IP models: how the layers line up,
what each layer is responsible for, what each layer adds/removes, and how
addressing works per layer.

**1. Differences between OSI and TCP/IP.** OSI is a seven-layer *reference*
model, mainly used to teach and reason about networking in general. TCP/IP is
the four-layer model that actually describes the protocol suite the Internet
runs on; several OSI layers (Application, Presentation, Session) collapse into
a single TCP/IP Application layer, and OSI's Data Link/Physical collapse into
TCP/IP's Network Access layer.

**2. Layer correspondence.**

| OSI (7 layers)      | TCP/IP (4 layers) |
|----------------------|--------------------|
| 7. Application        | Application        |
| 6. Presentation        | Application        |
| 5. Session              | Application        |
| 4. Transport            | Transport          |
| 3. Network               | Internet            |
| 2. Data Link              | Network Access      |
| 1. Physical                | Network Access      |

**3. Responsibility of each layer.**
- **Application** (OSI 7 / TCP-IP 4): provides network services directly to
  end-user software (HTTP, FTP, SMTP, DNS).
- **Presentation** (OSI 6): translates, encrypts, or compresses data between
  formats (e.g. text encoding, JPEG).
- **Session** (OSI 5): opens, maintains, and closes communication sessions
  between applications.
- **Transport** (OSI 4 / TCP-IP 3): end-to-end delivery, multiplexing via
  ports, reliability and flow control (TCP, UDP).
- **Network** (OSI 3 / TCP-IP 2): logical addressing and routing between
  networks (IP, ICMP).
- **Data Link** (OSI 2 / TCP-IP 1): framing and physical addressing within one
  network segment (MAC addresses, Ethernet).
- **Physical** (OSI 1 / TCP-IP 1): transmission of raw bits over cable,
  fiber, or radio.

**4. What each layer adds/removes.** Moving down the stack (sending), each
layer wraps the data from the layer above with its own header —
**encapsulation**: Transport adds a TCP/UDP header (ports), Network adds an IP
header (source/destination IP), Data Link adds a MAC header and trailer
(frame). Moving up the stack (receiving), each layer strips its own header
before passing the payload up — **decapsulation**.

**5. Addressing per layer.**

| Layer | Address type | Example |
|---|---|---|
| Application | Logical name (domain name) | `www.example.com`, resolved via DNS |
| Transport | Port number | 80 (HTTP), 443 (HTTPS) |
| Network | IP address | `192.168.1.10` |
| Data Link | MAC address | `00:1A:2B:3C:4D:5E` |
| Physical | No address (uses signals) | Electrical/optical/radio signaling |

Each layer's addressing is independent: the Network layer routes between
networks using IP addresses, while the Data Link layer only needs to identify
devices within the same local network using MAC addresses.

## Exercise 04: To Send a Package

**Task recap.** Explain, step by step, how a packet travels from Computer A
(`185.8.135.136`) to Computer B (`101.24.34.2`), and name which TCP/IP layers
are involved.

**1. Step-by-step journey.**
1. **Application (A):** an application on A prepares data addressed logically
   to B (e.g. by hostname/IP and port).
2. **Transport (A):** the OS wraps the data in a TCP or UDP segment, adding
   source and destination port numbers.
3. **Internet/Network (A):** the segment is wrapped in an IP packet with
   source IP `185.8.135.136` and destination IP `101.24.34.2`. The routing
   table on A determines the next hop (the default gateway, since B is on a
   different network).
4. **Network Access (A):** the packet is framed with the MAC address of the
   *next hop* (the gateway/router), not of B — Ethernet/Wi-Fi only needs a
   local, one-hop address — and transmitted onto the physical medium.
5. **Routing across the Internet:** each router along the path re-examines the
   IP header, looks up its own routing table for `101.24.34.2`, decrements the
   IP TTL, re-frames the packet with the MAC address of the *next* router (or
   of B, on the final hop), and forwards it. This repeats hop by hop until a
   router on B's own network delivers the frame to B directly.
6. **Network Access → Internet → Transport → Application (B):** B strips the
   frame header, then the IP header, then the TCP/UDP header, and delivers the
   original data to the application listening on the destination port.

**2. Layers involved.** All four TCP/IP layers participate: Application
(data), Transport (ports, TCP/UDP), Internet (IP addressing and per-hop
routing), and Network Access (framing and physical delivery for each
individual hop).

## Exercise 05: NAT

**Task recap.** Explain what NAT is, how it works, and when it is useful.

**1. What is NAT?** Network Address Translation is a technique, usually run on
a router/firewall at the edge of a private network, that rewrites the source
(and/or destination) IP address — and typically the port — of packets as they
cross between a private network and a public network.

**2. How does NAT work?** For outbound traffic, the NAT device replaces a
private source IP:port (e.g. `192.168.1.10:51000`) with its own public
IP:port (e.g. `203.0.113.5:40000`) and records the mapping in a translation
table. Return traffic addressed to the public IP:port is looked up in that
table and rewritten back to the original private IP:port before being
forwarded inside the LAN. This many-to-one form (many private IP:port pairs
sharing one public IP, distinguished by port) is often specifically called
PAT (Port Address Translation), but is commonly just called NAT.

**3. When is NAT useful?**
- It lets many devices on a private network share a single public IPv4
  address, which conserves scarce public IPv4 address space.
- It hides the internal network topology and addressing from the outside,
  which is a mild security/obscurity benefit.
- It is what makes home and office routers work: every device behind the
  router gets a private address, and only the router's single public address
  is visible to the Internet.
