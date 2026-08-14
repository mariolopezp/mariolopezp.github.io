# Dead Drop Resolver Lab

Personal cybersecurity laboratory for studying Dead Drop Resolver
architecture, Web Services, C2 communication patterns and detection.

## Current status

Phase 1 - GitHub Pages

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