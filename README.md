# Dead Drop Resolver Lab

Personal cybersecurity laboratory for studying Dead Drop Resolver
architecture, Web Services, C2 communication patterns and detection.

## Phase 1 - GitHub Pages

## Architecture

Client
   |
   | HTTPS GET
   v
GitHub Pages
   |
   v
tasks.json

## Current task format

{
    "task_id": "001",
    "type": "PING",
    "created": "2026-08-14T16:00:00Z"
}

## Observations

- GitHub Pages provides the resource over HTTPS.
- The client initiates the connection.
- The server does not need to know the client.
- Tasks can be changed by modifying the public JSON resource.



## Phase 1.1 - Network analysis

The initial request was performed using curl.

Observed flow:

1. DNS resolution of mariolopezp.github.io.
2. TCP connection to port 443.
3. TLS negotiation.
4. HTTP/1.1 selected through ALPN.
5. HTTP GET request to /dead-drop-resolver/tasks.json.
6. GitHub returned HTTP 200.
7. The response contained JSON.
8. GitHub infrastructure exposed caching-related headers.

The client initiates the connection and retrieves the resource over HTTPS.

