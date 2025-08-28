from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pyodbc
import pandas as pd
import io
import os

app = FastAPI()

# 允許跨域請求，這在前後端分離部署時是必要的
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 實際部署時請替換為前端網站的 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MSSQL 連線設定，從環境變數讀取以確保安全
DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING", "Driver={ODBC Driver 18 for SQL Server};Server=138.2.30.40,5857;Database=KPCOMP;UID=sa;PWD=Action282929;")

def get_db_connection():
    """建立並回傳資料庫連線"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to database: {e}")

def upsert_data_to_mssql(data: pd.DataFrame):
    """將 DataFrame 資料 Upsert 到 MSSQL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 逐筆處理，並使用參數化查詢來防止 SQL 注入
        for index, row in data.iterrows():
            store_name = row.get('StoreName')
            year = int(row.get('Year'))
            month = int(row.get('Month'))
            amount = float(row.get('Amount'))

            # 使用 IF EXISTS 實現 Upsert
            cursor.execute("""
                IF EXISTS (SELECT 1 FROM SalesData WHERE StoreName = ? AND Year = ? AND Month = ?)
                BEGIN
                    UPDATE SalesData SET Amount = ?, LastUpdated = GETDATE()
                    WHERE StoreName = ? AND Year = ? AND Month = ?
                END
                ELSE
                BEGIN
                    INSERT INTO SalesData (StoreName, Year, Month, Amount)
                    VALUES (?, ?, ?, ?)
                END
            """, store_name, year, month, amount, store_name, year, month, amount)
        
        conn.commit()
        return {"status": "success", "message": "Data synchronized successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database synchronization failed: {e}")
    finally:
        conn.close()

@app.post("/api/upload-file")
async def upload_and_sync_file(file: UploadFile = File(...)):
    """處理檔案上傳並同步資料"""
    try:
        file_extension = file.filename.split('.')[-1]
        contents = await file.read()
        
        if file_extension == 'csv':
            df = pd.read_csv(io.BytesIO(contents))
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        # 簡單的資料驗證
        required_columns = ['StoreName', 'Year', 'Month', 'Amount']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"Missing required columns. Please check your file headers.")
        
        return upsert_data_to_mssql(df)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {e}")

class ManualData(BaseModel):
    store_name: str
    year: int
    month: int
    amount: float

@app.post("/api/manual-sync")
async def sync_manual_data(items: List[ManualData]):
    """處理手動輸入資料並同步"""
    try:
        # 將 Pydantic 模型轉換為 DataFrame
        data_list = [item.dict() for item in items]
        df = pd.DataFrame(data_list)
        df.rename(columns={'store_name': 'StoreName', 'year': 'Year', 'month': 'Month', 'amount': 'Amount'}, inplace=True)
        
        return upsert_data_to_mssql(df)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual data synchronization failed: {e}")