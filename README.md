[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/e7FBMwSa)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21872536&assignment_repo_type=AssignmentRepo)
# EmoGo Backend

This is the backend server for the **EmoGo** mobile application, built with **FastAPI** and **MongoDB Atlas**. It handles data collection for Vlogs, Sentiments, and GPS coordinates.

## 🔗 Data Dashboard (Assignment Requirement)

**You can view, monitor, and download all collected data at the following URI:**

👉 **[https://emogo-backend-longyuju1116.onrender.com/dashboard](https://emogo-backend-longyuju1116.onrender.com/dashboard)**

### Dashboard Features:
1.  **View Data:** Real-time table view of GPS coordinates, Sentiments, and Vlogs.
2.  **Download CSV:** One-click export for all GPS and Sentiment logs.
3.  **Download ZIP:** One-click batch download for all MP4 Vlog files.
4.  **Video Playback:** Direct streaming of uploaded videos from the browser.

---

## 🛠 Tech Stack

* **Framework:** Python FastAPI
* **Database:** MongoDB Atlas (NoSQL)
* **File Storage:** MongoDB GridFS (for MP4 video storage)
* **Deployment:** Render.com

## 🚀 API Endpoints

* `GET /dashboard`: The researcher/admin interface.
* `POST /upload_data`: Receives JSON data (Sentiment & GPS).
* `POST /upload_vlog`: Receives video files (Multipart/form-data).
* `GET /export_csv`: Exports all text data to a single CSV file.
* `GET /export_zip`: bundles all video files into a ZIP archive.

## 📦 Local Development

To run this project locally:

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables:**
    Create a `.env` file or set `MONGO_URI` in your terminal.

3.  **Run the server:**
    ```bash
    uvicorn main:app --reload
    ```