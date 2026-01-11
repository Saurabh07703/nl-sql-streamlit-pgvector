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

## 3. (Optional) Connect GitHub for Automatic Deployment
To automatically update your Space whenever you push to GitHub:

1.  **Open Space Settings**:
    *   In your Hugging Face Space, click on the **Settings** button (top right).
2.  **Connect Repository**:
    *   Scroll down to the **Git** or **Assets** section (look for "Connect a repository").
    *   Click **Connect to GitHub**.
    *   Authorize Hugging Face if prompted.
    *   Select your GitHub repository (`your-username/your-repo`).
3.  **Setup Action**:
    *   Hugging Face will prompt you to "Configure the Action".
    *   It will open a **Pull Request** on your GitHub repository with a `.github/workflows/main.yml` file.
    *   **Merge** that Pull Request on GitHub.
4.  **Done!**:
    *   Now, every time you push code to GitHub, it will automatically sync to your Hugging Face Space.

