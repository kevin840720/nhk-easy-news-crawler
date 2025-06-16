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

app = FastAPI()

@app.get("/status")
async def status_check():
    return {"status": "ok"}

@app.api_route("/crawler/easy", methods=["GET", "POST"])
async def crawler_easy(request:Request,
                       start_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2024-06-01"),
                       end_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2024-06-02"),
                       ):
    # 處理 GET/POST 都要支援 form/query
    if request.method == "POST":
        form = await request.form()
        start_date = form.get("start_date", start_date)
        end_date = form.get("end_date", end_date)
    data = run_nhk_easy_crawler(start_date=start_date, end_date=end_date)
    return JSONResponse({"status": "success",
                         "count": len(data),
                         "data": data,
                         })

@app.api_route("/crawler/news", methods=["GET", "POST"])
async def crawler_news(request:Request,
                       start_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2024-06-01"),
                       end_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2024-06-02"),
                       ):
    if request.method == "POST":
        form = await request.form()
        start_date = form.get("start_date", start_date)
        end_date = form.get("end_date", end_date)
    data = run_nhk_crawler(start_date=start_date, end_date=end_date)
    return JSONResponse({"status": "success",
                         "count": len(data),
                         "data": data,
                         })

@app.api_route("/crawler/all", methods=["GET", "POST"])
async def crawler_all(request:Request,
                      start_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2024-06-01"),
                      end_date:str=Query(None, description="開始日期 (YYYY-MM-DD)", example="2024-06-02"),
                      ):
    if request.method == "POST":
        form = await request.form()
        start_date = form.get("start_date", start_date)
        end_date = form.get("end_date", end_date)
    data = run_nhk_crawler_all(start_date=start_date, end_date=end_date)
    return JSONResponse({"status": "success",
                         "count": len(data),
                         "data": data,
                         })
