import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# --- 設定 CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 連線 MongoDB ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["EmoGoDB"]
fs = gridfs.GridFS(db)

# --- 定義資料模型 ---
class DataItem(BaseModel):
    type: str
    content: dict
    timestamp: str

# =======================
# API 區域
# =======================

@app.get("/")
def read_root():
    return {"message": "EmoGo Backend is running!"}

@app.post("/upload_data")
def upload_data(item: DataItem):
    collection_name = "gps" if item.type == "gps" else "sentiments"
    # 插入資料時補上一個伺服器時間，方便排序
    data = item.dict()
    data["server_time"] = datetime.now()
    db[collection_name].insert_one(data)
    return {"status": "success", "msg": f"Saved to {collection_name}"}

@app.post("/upload_vlog")
async def upload_vlog(file: UploadFile = File(...)):
    file_id = fs.put(file.file, filename=file.filename, content_type=file.content_type)
    db.vlogs.insert_one({
        "filename": file.filename,
        "file_id": str(file_id),
        "description": "User Vlog",
        "server_time": datetime.now()
    })
    return {"status": "success", "file_id": str(file_id)}

@app.get("/video/{file_id}")
def stream_video(file_id: str):
    try:
        grid_out = fs.get(ObjectId(file_id))
        return StreamingResponse(
            grid_out, 
            media_type=grid_out.content_type,
            headers={"Content-Disposition": f"inline; filename={grid_out.filename}"}
        )
    except:
        raise HTTPException(status_code=404, detail="Video not found")

# =======================
# 🎨 升級版 Dashboard (黑白灰現代風)
# =======================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    # 撈取資料 (反向排序：最新的在上面)
    gps_data = list(db.gps.find({}, {"_id": 0}).sort("server_time", -1).limit(20))
    sentiment_data = list(db.sentiments.find({}, {"_id": 0}).sort("server_time", -1).limit(20))
    vlogs = list(db.vlogs.find({}, {"_id": 0, "file_id": 1, "filename": 1, "server_time": 1}).sort("server_time", -1))

    # --- 1. 產生 Vlog HTML ---
    vlog_rows = ""
    if not vlogs:
        vlog_rows = "<tr><td colspan='3' style='text-align:center; color:#999;'>No vlogs uploaded yet.</td></tr>"
    else:
        for v in vlogs:
            f_id = v.get('file_id')
            f_name = v.get('filename', 'Unknown')
            t_stamp = v.get('server_time', '').strftime('%Y-%m-%d %H:%M') if v.get('server_time') else 'N/A'
            vlog_rows += f"""
            <tr>
                <td>{t_stamp}</td>
                <td>{f_name}</td>
                <td style="text-align:right;">
                    <a href="/video/{f_id}" target="_blank" class="btn">Play / Download</a>
                </td>
            </tr>
            """

    # --- 2. 產生 Sentiment HTML ---
    sent_rows = ""
    if not sentiment_data:
        sent_rows = "<tr><td colspan='2' style='text-align:center; color:#999;'>No sentiments data.</td></tr>"
    else:
        for s in sentiment_data:
            t = s.get('timestamp', 'N/A').replace('T', ' ').split('.')[0]
            # 假設 content 裡有 mood，如果沒有就顯示整個 content
            content_str = str(s.get('content', {}))
            sent_rows += f"<tr><td>{t}</td><td>{content_str}</td></tr>"

    # --- 3. 產生 GPS HTML (加地圖連結) ---
    gps_rows = ""
    if not gps_data:
        gps_rows = "<tr><td colspan='3' style='text-align:center; color:#999;'>No GPS data.</td></tr>"
    else:
        for g in gps_data:
            t = g.get('timestamp', 'N/A').replace('T', ' ').split('.')[0]
            content = g.get('content', {})
            lat = content.get('lat', 0)
            lon = content.get('lon', 0)
            map_link = f"https://www.google.com/maps?q={lat},{lon}"
            
            gps_rows += f"""
            <tr>
                <td>{t}</td>
                <td>{lat:.5f}, {lon:.5f}</td>
                <td style="text-align:right;">
                    <a href="{map_link}" target="_blank" class="link-btn">Map ↗</a>
                </td>
            </tr>
            """

    # --- 4. 組合最終 HTML (包含 CSS) ---
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EmoGo Data Center</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="10">
        <style>
            /* Reset & Basic Setup */
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #fafafa; /* 淺灰背景 */
                color: #333;
                line-height: 1.6;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
            }}
            
            /* Header */
            header {{
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            h1 {{ font-weight: 700; letter-spacing: -0.5px; font-size: 24px; }}
            .badge {{
                background: #000;
                color: #fff;
                padding: 4px 12px;
                border-radius: 99px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}

            /* Cards */
            .card {{
                background: #ffffff;
                border: 1px solid #e5e5e5;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            }}
            h2 {{
                font-size: 18px;
                margin-bottom: 16px;
                font-weight: 600;
                color: #111;
            }}

            /* Tables */
            table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
            th {{ 
                text-align: left; 
                color: #888; 
                font-weight: 500; 
                text-transform: uppercase; 
                font-size: 12px;
                padding-bottom: 12px;
                border-bottom: 2px solid #f0f0f0;
            }}
            td {{ 
                padding: 16px 0; 
                border-bottom: 1px solid #f5f5f5; 
                vertical-align: middle;
            }}
            tr:last-child td {{ border-bottom: none; }}

            /* Buttons & Links */
            .btn {{
                background-color: #000;
                color: #fff;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                transition: opacity 0.2s;
            }}
            .btn:hover {{ opacity: 0.8; }}
            
            .link-btn {{
                color: #555;
                text-decoration: none;
                border: 1px solid #ddd;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
            }}
            .link-btn:hover {{ border-color: #000; color: #000; }}

        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>EmoGo Data Center</h1>
                <span class="badge">Live Connection</span>
            </header>

            <div class="card">
                <h2>🎥 Collected Vlogs</h2>
                <table>
                    <thead>
                        <tr>
                            <th width="30%">Time</th>
                            <th width="40%">Filename</th>
                            <th width="30%" style="text-align:right;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {vlog_rows}
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>❤️ Sentiments Log</h2>
                <table>
                    <thead>
                        <tr>
                            <th width="30%">Time</th>
                            <th>Data Content</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sent_rows}
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>📍 GPS Tracking</h2>
                <table>
                    <thead>
                        <tr>
                            <th width="30%">Time</th>
                            <th width="40%">Coordinates</th>
                            <th width="30%" style="text-align:right;">Location</th>
                        </tr>
                    </thead>
                    <tbody>
                        {gps_rows}
                    </tbody>
                </table>
            </div>
            
            <p style="text-align: center; color: #999; font-size: 12px; margin-top: 40px;">
                EmoGo Backend v1.0 • Deployed on Render
            </p>
        </div>
    </body>
    </html>
    """
    return html_content