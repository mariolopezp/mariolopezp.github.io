# Dead Drop Resolver Lab

A personal home-lab project designed to study, through hands-on implementation, concepts related to:

* Client-server architectures
* HTTP/HTTPS
* Polling and beaconing
* REST APIs
* Distributed systems
* State persistence
* Task management
* Machine-to-machine communication
* Logging and observability
* Error handling and retries
* Task/response protocols
* Authentication and integrity
* Agent behavior and detection

The lab consists of a Raspberry Pi, a Windows computer, and GitHub Pages acting as the *dead drop* infrastructure.

> **Note:** This project is developed in a controlled home laboratory environment for educational purposes.

---

# 1. Architecture

The initial architecture consists of three main components:

```text
                         INTERNET
                            │
                            │ HTTPS
                            ▼
                  ┌────────────────────┐
                  │    GitHub Pages    │
                  │                    │
                  │     tasks.json     │
                  └─────────┬──────────┘
                            │
                            │ GET
                            │
                            ▼
                  ┌────────────────────┐
                  │    Raspberry Pi    │
                  │                    │
                  │     (Resolver)     │
                  │                    │
                  │      Poller        │
                  │      Flask API     │
                  └─────────┬──────────┘
                            │
                            │ HTTP / LAN
                            │
                            ▼
                  ┌────────────────────┐
                  │      Windows       │
                  │                    │
                  │    Windows Agent   │
                  │                    │
                  │    Dispatcher      │
                  │     Handlers       │
                  └────────────────────┘
```

The architecture can be divided into two communication channels.

### External channel

```text
Raspberry Pi
     │
     │ HTTPS
     ▼
GitHub Pages
```

The Raspberry Pi periodically retrieves a resource hosted on GitHub Pages.

### Internal channel

```text
Windows Agent
     │
     │ HTTP
     ▼
Raspberry Flask API
```

The Windows Agent retrieves tasks through the Flask API running on the Raspberry Pi.

---

# 2. Dead Drop Concept

A *dead drop* is a communication mechanism where the sender and receiver do not need to establish a direct connection with each other. The C2 server is actually hidden inside trusted websites or legitimate third-party cloud services.

In this lab:

```text
          ┌──────────────────┐
          │   GitHub Pages   │
          │                  │
          │   tasks.json     │
          └────────┬─────────┘
                   │
                   │ GET
                   ▼
             Raspberry Pi
```

GitHub Pages does not need to know that the Raspberry Pi exists, it only serves a resource publicly over  the internet.

The Raspberry Pi (which acts as the resolver) decides when to retrieve that resource:

```text
Raspberry
    │
    ├── GET tasks.json
    │
    ├── Parse response
    │
    ├── Validate task
    │
    └── Determine whether a new task exists
```


# 3. GitHub Pages

GitHub Pages acts as the dead drop, being the main resource:

```text
tasks.json
```

Example:

```json
{
    "task_id": "001",
    "type": "PING",
    "created": "2026-08-14T16:00:00Z"
}
```

The Raspberry Pi performs an HTTPS request:

```http
GET /dead-drop-resolver/tasks.json
```

GitHub Pages responds with:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

followed by the JSON content.

---

# 4. HTTPS Communication Analysis

One of the first tests was performed using `curl` in verbose mode.

The observed communication can be represented as:

```text
DNS
 │
 │ mariolopezp.github.io
 ▼
GitHub IP
 │
 ▼
TCP 443
 │
 ▼
TLS
 │
 ▼
HTTP/1.1
 │
 ▼
GET /dead-drop-resolver/tasks.json
 │
 ▼
HTTP 200 OK
 │
 ▼
JSON
```

The study of the request allowed the following concepts to be observed:

* DNS resolution
* TCP connection establishment
* TLS negotiation
* HTTP version negotiation
* HTTP request/response
* JSON content delivery
* HTTP caching headers

---

# 5. Raspberry Pi — Dead Drop Resolver

The Raspberry Pi is the intermediate component of the system.

Its responsibilities are:

1. Poll GitHub Pages.
2. Retrieve the JSON resource.
3. Validate the task.
4. Compare the remote `task_id` with local state.
5. Detect new tasks.
6. Record relevant events.
7. Expose the current task through Flask.
8. Eventually receive task results from the Windows Agent.

Architecture:

```text
                    Raspberry Pi
          ┌────────────────────────────┐
          │                            │
          │      Dead Drop Resolver    │
          │                            │
GitHub ──►│ Poller                     │
          │    │                       │
          │    ▼                       │
          │ Task validation            │
          │    │                       │
          │    ▼                       │
          │ Shared task state          │
          │    │                       │
          │    ▼                       │
          │ Flask API                  │
          │    │                       │
          └────┼───────────────────────┘
               │
               ▼
           Windows
```

---

# 6. Polling

The resolver uses periodic polling.

```text
        ┌─────────────────┐
        │                 │
        │   GET GitHub    │
        │                 │
        └────────┬────────┘
                 │
                 ▼
           Process task
                 │
                 ▼
              Logging
                 │
                 ▼
               Sleep
                 │
                 │
                 └──────────────┐
                                │
                                ▼
                           GET GitHub
```

The polling interval is configurable.

This provides an opportunity to study concepts such as:

* Polling
* Beaconing
* Periodicity
* Jitter
* Network telemetry
* Behavioral detection

---

# 7. Local State

The resolver maintains local state to avoid processing the same task repeatedly.

Conceptually:

```text
Remote task_id
       │
       ▼
      "002"
       │
       │ compare
       ▼
Local last_task_id
       │
       ▼
      "001"
```

Because the values are different:

```text
New task detected
```

The local state is then updated:

```text
last_task_id = 002
```

On the next polling cycle:

```text
Remote: 002
Local:  002
```

The result is:

```text
No new task
```

---

# 8. Logging

The resolver records relevant events.

Examples include:

```text
INFO poll_success
INFO no_new_task
INFO task_received
ERROR poll_error
```

Example log entry:

```text
<timestamp> INFO task_received task_id: 002 task_type: STATUS
```

This makes it possible to distinguish between:

* Successful communication
* No new task being available
* A new task being received
* Communication errors

---

# 9. systemd Integration

Once the resolver was working correctly, it was configured as a persistent Linux service using `systemd`.

Architecture:

```text
Raspberry boot
      │
      ▼
    systemd
      │
      ▼
dead-drop-resolver.service
      │
      ▼
 resolver.py
```

The service is responsible for:

* Starting automatically
* Running the resolver without an interactive SSH session
* Using the project's Python virtual environment
* Restarting the process if it fails

Which allows the resolver to operate continuously as a background service, and not having to launch every script manually from the Rapsberry pi.

---

# 10. Flask API

The next component added to the Raspberry Pi was a Flask API. Its purpose is to provide an interface between the resolver and the Windows Agent.

```text
GitHub
   │
   ▼
Poller
   │
   ▼
Current task
   │
   ▼
Flask
   │
   │ GET /task
   ▼
Windows Agent
```

The polling loop and Flask server run concurrently.

Conceptually:

```text
                 resolver.py
                      │
             ┌────────┴────────┐
             │                 │
             ▼                 ▼
          Poller             Flask
             │                 │
             │                 │
             ▼                 │
       current_task ◄──────────┘
```

Because both components access shared state, concurrency must be considered when reading or modifying the current task.

---

# 11. `/task` Endpoint

The first Flask API endpoint is:

```http
GET /task
```

Its purpose is to provide the Windows Agent with the currently available task.

Example response:

```json
{
    "task_id": "002",
    "type": "PING",
    "created": "2026-08-15T20:00:00Z"
}
```

The complete communication flow is:

```text
Windows Agent
      │
      │ GET /task
      ▼
Raspberry:8080
      │
      ▼
current_task
      │
      ▼
JSON response
      │
      ▼
Windows Agent
```

The endpoint was initially tested from Windows using `curl`.

---

# 12. Windows Agent

The Windows Agent is responsible for consuming and processing tasks provided by the Raspberry Pi.

Its responsibilities are:

1. Query the Raspberry Flask API.
2. Receive a task.
3. Validate its structure.
4. Check local state.
5. Pass the task to the dispatcher.
6. Execute the appropriate handler.
7. Generate a result.
8. Eventually send the result back to the Raspberry.

Architecture:

```text
             Raspberry
                 │
                 │ GET /task
                 ▼
        ┌──────────────────┐
        │  Windows Agent   │
        │                  │
        │     Client       │
        │       │          │
        │       ▼          │
        │    Dispatcher    │
        │       │          │
        │       ▼          │
        │    Handlers      │
        └──────────────────┘
```

---

# 13. Dispatcher

The dispatcher separates task reception from task implementation.

For example:

```text
Task
 │
 │ type
 ▼
Dispatcher
 │
 ├── PING
 │     └── ping handler
 │
 ├── STATUS
 │     └── status handler
 │
 └── TIME
       └── time handler
```

This architecture makes it possible to add new task types without significantly modifying the main agent loop. In case of adding a new task, a new case with a new type_id should be included in the dispatcher, and then within the handlers, the code that needs to be executed within the Windows Agent to perform the task.

---

# 14. PING Task

The first task implemented was `PING`.

Flow:

```text
GitHub
   │
   ▼
Raspberry
   │
   │ task
   ▼
Windows Agent
   │
   ▼
Dispatcher
   │
   ▼
PING handler
```

The purpose of this task is mainly to validate the complete task-delivery pipeline. It succesfully performs a ping request to www.google.com

---

# 15. Remote Execution Task

A second task was implemented to study controlled remote execution within the laboratory environment.

Conceptually:

```text
Raspberry
    │
    │ task
    ▼
Windows Agent
    │
    ▼
Task dispatcher
    │
    ▼
Controlled execution
    │
    ▼
Result
```

This provides a practical environment for studying concepts such as:

* Remote task execution
* Command-and-control architectures
* Agent behavior
* Bidirectional communication
* Process telemetry
* Network telemetry
* Detection opportunities

The functionality is intended exclusively for systems controlled by the project owner within the laboratory environment.

---

# 16. Current End-to-End Flow

The system currently operates approximately as follows:

```text
                    ┌─────────────────┐
                    │  GitHub Pages   │
                    │                 │
                    │   tasks.json    │
                    └────────┬────────┘
                             │
                             │ HTTPS
                             │
                             ▼
                    ┌─────────────────┐
                    │   Raspberry Pi  │
                    │                 │
                    │     Poller      │
                    │        │        │
                    │        ▼        │
                    │  current_task   │
                    │        │        │
                    │        ▼        │
                    │     Flask       │
                    └────────┬────────┘
                             │
                             │ HTTP
                             │ GET /task
                             ▼
                    ┌─────────────────┐
                    │     Windows     │
                    │                 │
                    │  Windows Agent  │
                    │        │        │
                    │        ▼        │
                    │   Dispatcher    │
                    │        │        │
                    │        ▼        │
                    │    Handler      │
                    └─────────────────┘
```

---

# 17. Current Project Status

| Component              | Status |
| ---------------------- | ------ |
| GitHub Pages dead drop | ✅      |
| `tasks.json`           | ✅      |
| HTTPS polling          | ✅      |
| Task validation        | ✅      |
| Persistent local state | ✅      |
| Logging                | ✅      |
| Polling loop           | ✅      |
| systemd                | ✅      |
| Flask API              | ✅      |
| `GET /task`            | ✅      |
| Windows Agent          | ✅      |
| Task dispatcher        | ✅      |
| PING task              | ✅      |
| REVERSE SSH       task | ✅      |
| `POST /result`         | ⏳      |

---

# 18. Next Objective — `POST /result`

The next step is to turn the current one-way task delivery:

```text
Raspberry
    │
    │ GET /task
    ▼
Windows
```

into a bidirectional task/response protocol:

```text
             Raspberry
                 │
                 │ GET /task
                 ▼
             Windows
                 │
                 │ process
                 ▼
               result
                 │
                 │ POST /result
                 ▼
             Raspberry
```

The planned endpoint is:

```http
POST /result
```

with a message similar to:

```json
{
    "task_id": "002",
    "status": "COMPLETED",
    "result": "Result of the execution"
}
```

# 19. Future Experiments

The main purpose of this project is not simply to make the system work, but to use it as a controlled laboratory.

### Connectivity loss

```text
Windows ─────X───── Raspberry
```

Investigate:

* Timeouts
* Retries
* Task state
* Recovery behavior

### Raspberry restart

```text
Raspberry
    │
    X
  reboot
```

Investigate state persistence and recovery.

### Windows restart

Determine what happens when the agent is restarted while processing a task.

### Duplicate task

```text
003
003
```

Study idempotency and duplicate processing.

### Duplicate result

```text
POST /result 003
POST /result 003
```

Determine how the server should handle repeated results.

### Unauthorized agent

Send a request from a different client and investigate how the Raspberry should identify and authorize agents.

### Task manipulation

Modify the content of a task and investigate how integrity mechanisms could detect tampering.

---

# 20. Final Learning Objectives

The final goal of the laboratory is to understand both how an agent-based communication system can be implemented and what evidence its behavior generates.

The conceptual architecture is:

```text
             DEAD DROP
                 │
                 ▼
            RESOLVER
                 │
                 ▼
              AGENT
                 │
                 ▼
              RESULT
                 │
                 ▼
             RESOLVER
```

From this architecture, the project can later be used to study:

```text
Network telemetry
       │
       ├── DNS
       ├── TCP
       ├── HTTP
       └── HTTPS

Host telemetry
       │
       ├── Processes
       ├── Network connections
       ├── Files
       └── Logs

Detection
       │
       ├── Behavioral rules
       ├── Sigma
       ├── YARA
       ├── IOCs
       └── Correlation
```
