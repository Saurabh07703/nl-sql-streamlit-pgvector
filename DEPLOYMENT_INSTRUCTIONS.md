# Deployment Instructions: Hugging Face Spaces

We are deploying to **Hugging Face Spaces** for better performance and native Streamlit support.

## 1. Cloud Database Setup (PostgreSQL)
Ensure you have a cloud database (like Neon.tech) as previously configured.
*   **Connection String**: You will need your `postgres://...` URL.
*   **Access**: Ensure the database allows connections from the internet (0.0.0.0/0).

## 2. Deploy to Hugging Face Spaces

1.  **Create a Space**:
    *   Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click "Create new Space".
    *   **Space name**: `nl-sql-streamlit` (or similar).
    *   **License**: MIT (or your choice).
    *   **SDK**: Select **Streamlit**.
    *   Click "Create Space".

2.  **Upload Code**:
    *   **Option A: Git (Recommended)**
        *   Clone your new Space locally: `git clone https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`
        *   Copy all your project files into that folder.
        *   `git add .`, `git commit -m "Initial commit"`, `git push`.
    *   **Option B: Web Upload**
        *   On the Space page, go to "Files".
        *   Upload all files (`app/`, `db/`, `requirements.txt`, `README.md`, etc.).

3.  **Configure Environment Variables (Secrets)**:
    *   Go to **Settings** in your Space.
    *   Scroll to **Variables and secrets**.
    *   Click **New secret**.
    *   **Name**: `DATABASE_URL`
    *   **Value**: Paste your full PostgreSQL connection string.
    *   *(If you have other API keys, add them here too).*

4.  **Verify**:
    *   The "App" tab will show "Building".
    *   Once "Running", your app is live!


---
**Note**: The custom `README.md` configuration we added handles the build settings automatically.

## 3. Connect GitHub for Automatic Deployment (Manual Method)
Since the "Connect to GitHub" button is not visible, we will set up a **GitHub Action** manually.

1.  **Get a Hugging Face Access Token**:
    *   Go to your [Hugging Face Settings -> Access Tokens](https://huggingface.co/settings/tokens).
    *   Create a new token with **Write** permissions.
    *   Copy the token.

2.  **Add Secret to GitHub**:
    *   Go to your GitHub Repository.
    *   Click **Settings** -> **Secrets and variables** -> **Actions**.
    *   Click **New repository secret**.
    *   **Name**: `HF_TOKEN`
    *   **Value**: Paste your Hugging Face token.
    *   Click **Add secret**.

3.  **Configure the Sync Workflow**:
    *   Open the file `.github/workflows/sync_to_hub.yml` in your project.
    *   **Edit the last line** to match your Hugging Face Space URL.
    *   Replace `YOUR_HF_USERNAME/YOUR_SPACE_NAME` with your actual Space path (e.g., `saurabh/nl-sql-streamlit`).
    *   *Example*: `git push https://oauth2:$HF_TOKEN@huggingface.co/spaces/saurabh/nl-sql-streamlit main`

4.  **Push Changes**:
    *   Commit and push your changes to GitHub.
    *   The Action will run and sync your code to Hugging Face automatically!

