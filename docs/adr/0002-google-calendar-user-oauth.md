# Google Calendar User OAuth

The first calendar integration uses the owner's Google Calendar through user OAuth with read-only scope and a refresh token persisted in the Docker data volume. We chose this over a service account because the assistant reads a personal calendar, and user OAuth more naturally represents the owner's actual calendar access without requiring calendar sharing setup.

**Consequences**

- The NAS deployment needs a one-time authorization step before unattended runs work.
- The persisted token is sensitive operational data and must live outside the committed repository.
