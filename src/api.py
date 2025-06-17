# -*- encoding: utf-8 -*-
"""
@File    :  app.py
@Time    :  2025/06/16 18:39:44
@Author  :  Kevin Wang
@Desc    :  None
"""

from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from main import (
    run_nhk_crawler,
    run_nhk_crawler_all,
    run_nhk_easy_crawler,
)

app = FastAPI(
    title="NHK Crawler API",
    description="提供 NHK 日文新聞的爬蟲",
    version="1.0.0"
)

@app.get("/status")
async def status_check():
    return {"status": "ok"}

@app.api_route("/crawler/easy", methods=["GET", "POST"])
async def crawler_easy(request:Request,
                       start_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2025-06-01"),
                       end_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2025-06-02"),
                       ):
    if request.method == "POST":
        body = await request.body()
        if not body:
            return JSONResponse(status_code=400, content={"detail": "Missing JSON body"})
        json_data = await request.json()
        start_date = json_data.get("start_date", start_date)
        end_date = json_data.get("end_date", end_date)
    data = run_nhk_easy_crawler(start_date=start_date, end_date=end_date)
    return JSONResponse({"status": "success",
                         "count": len(data),
                         "data": data,
                         })

@app.api_route("/crawler/news", methods=["GET", "POST"])
async def crawler_news(request:Request,
                       start_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2025-06-01"),
                       end_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2025-06-02"),
                       ):
    if request.method == "POST":
        body = await request.body()
        if not body:
            return JSONResponse(status_code=400, content={"detail": "Missing JSON body"})
        json_data = await request.json()
        start_date = json_data.get("start_date", start_date)
        end_date = json_data.get("end_date", end_date)
    data = run_nhk_crawler(start_date=start_date, end_date=end_date)
    return JSONResponse({"status": "success",
                         "count": len(data),
                         "data": data,
                         })

@app.api_route("/crawler/all", methods=["GET", "POST"])
async def crawler_all(request:Request,
                      start_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2025-06-01"),
                      end_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2025-06-02"),
                      ):
    if request.method == "POST":
        body = await request.body()
        if not body:
            return JSONResponse(status_code=400, content={"detail": "Missing JSON body"})
        json_data = await request.json()
        start_date = json_data.get("start_date", start_date)
        end_date = json_data.get("end_date", end_date)
    data = run_nhk_crawler_all(start_date=start_date, end_date=end_date)
    return JSONResponse({"status": "success",
                         "count": len(data),
                         "data": data,
                         })
