# app.py
from flask import Flask, request, jsonify
from main import run_nhk_easy_crawler, run_nhk_crawler

def get_dates():
    # GET/POST 一樣從 values 取
    return request.values.get("start_date"), request.values.get("end_date")

app = Flask(__name__)
app.json.ensure_ascii = False   # 關掉 unicode escape

@app.route("/crawler/easy", methods=["GET","POST"])
def crawler_easy():
    start_date, end_date = get_dates()
    data = run_nhk_crawler(start_date=start_date,
                           end_date=end_date,
                           )
    return jsonify(status="success",
                   count=len(data),
                   data=data,
                   )

@app.route("/crawler/news", methods=["GET","POST"])
def crawler_news():
    start_date, end_date = get_dates()
    data = run_nhk_crawler(start_date=start_date,
                           end_date=end_date,
                           )
    return jsonify(status="success",
                   count=len(data),
                   data=data,
                   )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=41260, debug=True)
