from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import requests
import io
import os

app = FastAPI()

# 允許跨域請求，這在前後端分離部署時是必要的
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vue-fastapi-budgettargets.onrender.com"],  # 實際部署時請替換為前端網站的 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google App Script Web App 網址，從環境變數讀取
APP_SCRIPT_URL = os.environ.get("APP_SCRIPT_URL")

# 如果沒有設定環境變數，則使用這個預設值
if not APP_SCRIPT_URL:
    raise RuntimeError("APP_SCRIPT_URL environment variable is not set.")

def sync_data_to_sheets(data: pd.DataFrame):
    """將 DataFrame 資料發送到 Google App Script Web App"""
    try:
        # 轉換 DataFrame 為 JSON 格式，以便傳送
        json_data = data.to_dict(orient='records')
        
        # 發送 POST 請求
        response = requests.post(APP_SCRIPT_URL, json=json_data)
        
        # 檢查 HTTP 請求是否成功
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"Failed to send data to Google App Script: {req_err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

class ManualData(BaseModel):
    store_name: str
    year: int
    month: int
    amount: float

@app.post("/api/upload-file")
async def upload_and_sync_file(file: UploadFile = File(...)):
    """接收 CSV/Excel 檔案，解析後同步至 Google Sheets"""
    try:
        file_extension = file.filename.split('.')[-1].lower()
        contents = await file.read()
        
        if file_extension == 'csv':
            df = pd.read_csv(io.BytesIO(contents))
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a .csv or .xlsx file.")

        # 檢查必要的欄位是否存在
        required_columns = ['StoreName', 'Year', 'Month', 'Amount']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"Missing required columns. Please check your file headers. Required: {', '.join(required_columns)}")
        
        # 確保資料格式正確
        df['StoreName'] = df['StoreName'].astype(str)
        df['Year'] = df['Year'].astype(int)
        df['Month'] = df['Month'].astype(int)
        df['Amount'] = df['Amount'].astype(float)
        
        return sync_data_to_sheets(df)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {e}")

@app.post("/api/manual-sync")
async def sync_manual_data(items: List[ManualData]):
    """接收手動輸入的資料，同步至 Google Sheets"""
    try:
        # 將 Pydantic 模型轉換為 DataFrame
        data_list = [item.dict() for item in items]
        df = pd.DataFrame(data_list)
        df.rename(columns={'store_name': 'StoreName', 'year': 'Year', 'month': 'Month', 'amount': 'Amount'}, inplace=True)
        
        # 確保資料格式正確
        df['StoreName'] = df['StoreName'].astype(str)
        df['Year'] = df['Year'].astype(int)
        df['Month'] = df['Month'].astype(int)
        df['Amount'] = df['Amount'].astype(float)
        
        return sync_data_to_sheets(df)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual data synchronization failed: {e}")