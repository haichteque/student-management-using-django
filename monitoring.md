# Monitoring Setup Guide (New Relic)

This project uses **New Relic** for real-time performance monitoring and error tracking. This fulfills the "Monitoring and Error Tracking" requirement of the project rubrics.

## 1. What are we monitoring?

New Relic provides:
-   **APM (Application Performance Monitoring)**: Response times, throughput, and error rates.
-   **Transaction Traces**: Detailed breakdown of slow requests (SQL queries, external calls).
-   **Error Analytics**: Stack traces and frequency of exceptions.

## 2. How to Setup New Relic

1.  **Sign Up**: Go to [newrelic.com](https://newrelic.com/signup) and create a free account.
2.  **Get License Key**:
    -   Go to **API Keys** in your account settings.
    -   Copy the **INGEST - LICENSE** key.

## 3. Configuration

### Local Development
Add the key to your `.env` file:
```bash
NEW_RELIC_LICENSE_KEY=your_license_key_here
NEW_RELIC_APP_NAME="Student Management System (Local)"
```

### Production / Staging (Oracle Cloud)
The CI/CD pipeline is already configured to pass these variables. You just need to add the secret to GitHub.

-   **GitHub Secret Name**: `NEW_RELIC_LICENSE_KEY`
-   **Value**: (Your License Key)

The pipeline automatically sets the app name to:
-   `Student Management System (Staging)`
-   `Student Management System (Production)`
