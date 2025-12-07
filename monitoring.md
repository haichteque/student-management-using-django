# Monitoring Setup Guide (Sentry)

This project uses **Sentry** for real-time error tracking and performance monitoring. This fulfills the "Monitoring and Error Tracking" requirement of the project rubrics.

## 1. What are we monitoring?

We have configured Sentry to capture:

1.  **Error Tracking (Exceptions)**:
    -   **Crashes**: Any unhandled exception (e.g., `500 Internal Server Error`) is immediately reported.
    -   **Context**: Stack traces, request data (URL, parameters), and user details (if logged in) are attached to every error.
    -   **Alerts**: You get notified (email/Slack) when new bugs appear.

2.  **Performance Monitoring (Tracing)**:
    -   **Transactions**: We capture 100% of transactions (`traces_sample_rate=1.0`).
    -   **Metrics**: API response times, database query durations, and page load speeds.
    -   **Bottlenecks**: Identify slow views or inefficient SQL queries.

## 2. How to Create a Sentry Project

Follow these steps to generate your `SENTRY_DSN`:

1.  **Sign Up**: Go to [sentry.io](https://sentry.io/signup/) and create a free account.
2.  **Create Project**:
    -   Click **"Create Project"**.
    -   Choose Platform: **Django**.
    -   Set Alert Frequency: "Alert me on every new issue".
    -   Name your project (e.g., `student-management-system`).
    -   Click **"Create Project"**.
3.  **Get DSN**:
    -   You will be shown a "Configure Django" page.
    -   Look for the `DSN` (Data Source Name). It looks like: `https://examplePublicKey@o0.ingest.sentry.io/0`.
    -   **Copy this URL**.

## 3. Configuration

### Local Development
Add the DSN to your `.env` file:
```bash
SENTRY_DSN=https://your_public_key@o0.ingest.sentry.io/project_id
```

### Production / Staging (Oracle Cloud)
Add the environment variable to your Docker run command or CI/CD secrets:
-   **Key**: `SENTRY_DSN`
-   **Value**: `https://your_public_key@o0.ingest.sentry.io/project_id`
