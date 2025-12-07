# How to Stage and Deploy

This project uses a branch-based CI/CD workflow to manage deployments to Staging and Production environments.

## Overview

- **Staging Environment**:
  - **Branch**: `staging`
  - **URL**: `http://<VM_IP>:8001`
  - **Container Name**: `student-app-staging`

- **Production Environment**:
  - **Branch**: `main`
  - **URL**: `http://<VM_IP>:8000`
  - **Container Name**: `student-app`

## 1. Deploying to Staging

Use the staging environment to test changes before they go live.

1.  **Switch to the staging branch**:
    ```bash
    git checkout staging
    ```

2.  **Bring in your changes**:
    Merge your feature branch or commit changes directly.
    ```bash
    git merge my-feature-branch
    ```

3.  **Trigger Deployment**:
    Push the branch to GitHub.
    ```bash
    git push origin staging
    ```
    This triggers the `deploy-staging` job in the CI/CD pipeline.

4.  **Verify**:
    Once the job completes, access the application at `http://<VM_IP>:8001`.

## 2. Deploying to Production

Once changes are verified on Staging, promote them to Production.

1.  **Switch to the main branch**:
    ```bash
    git checkout main
    ```

2.  **Merge Staging**:
    ```bash
    git merge staging
    ```

3.  **Trigger Deployment**:
    Push the branch to GitHub.
    ```bash
    git push origin main
    ```
    This triggers the `deploy-production` job.

4.  **Verify**:
    Access the live application at `http://<VM_IP>:8000`.

## Troubleshooting

- **Check Actions Logs**: If a deployment fails, check the "Actions" tab in GitHub.
- **VM Logs**: SSH into the VM and check container logs if needed:
  ```bash
  docker logs student-app-staging  # For staging
  docker logs student-app          # For production
  ```
