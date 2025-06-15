# -*- encoding: utf-8 -*-
"""
@File    :  app.py
@Time    :  2025/06/16 06:49:57
@Author  :  Kevin Wang
@Desc    :  None
"""

from flask import Flask, jsonify, request
from main import run_crawler

app = Flask(__name__)

@app.route("/")
def index():
    return "NHK Easy News Crawler is running."

@app.route("/run-crawler", methods=["POST"])
def run_crawler_api():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    count = run_crawler(start_date=start_date, end_date=end_date)
    return jsonify({"status": "success", "inserted_news_count": count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=41260)
