# Deployment Instructions

Your application is now ready for deployment! Since this is a database-backed application, there are two main parts to deploying it:

## 1. Cloud Database Setup (PostgreSQL)
You cannot use `localhost` for a web deployment. You need a cloud-hosted PostgreSQL database.
**Recommendation**: Use [Neon.tech](https://neon.tech) (Free tier available).

1.  **Create a Project**: Sign up at Neon.tech and create a new project.
2.  **Get Connection String**: Copy the connection string (it looks like `postgres://user:pass@host/db`).
3.  **Enable pgvector**: Run this SQL command in the Neon SQL Editor:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```
4.  **Initialize Database**:
    *   Run the contents of `db/init_schema.sql` in the SQL Editor.
    *   (Optional) Run `db/seed_data.sql` to add sample data.

## 2. Deploy Code to Streamlit Community Cloud
This is the easiest way to host Streamlit apps.

1.  **Push to GitHub**:
    *   Create a new repository on GitHub.
    *   Run these commands in your terminal (if not already done):
        ```bash
        git init
        git add .
        git commit -m "Prepare for deployment"
        git branch -M main
        git remote add origin <your-github-repo-url>
        git push -u origin main
        ```
2.  **Deploy on Streamlit**:
    *   Go to [share.streamlit.io](https://share.streamlit.io/).
    *   Click "New App".
    *   Select your repository.
    *   **Main file path**: `app/main.py`
    *   **Click "Advanced Settings"**:
        *   Go to "Secrets".
        *   Paste your Cloud Database connection string:
            ```toml
            DATABASE_URL = "postgres://user:pass@host/dbname?sslmode=require"
            ```
    *   Click "Deploy".

## 3. Alternative: Render.com
If you prefer Render:
1.  Create a "Web Service".
2.  Connect GitHub repo.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `streamlit run app/main.py`
5.  **Environment Variables**: Add `DATABASE_URL` with your cloud DB value.
