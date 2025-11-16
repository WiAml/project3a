from flask import Flask, render_template, request
import pandas as pd
import pygal
import requests
import os
from datetime import datetime, date

app = Flask(__name__)
# Load symbols from stocks.csv
def load_symbols(csv_path="stocks.csv"):
    try:
        df =pd.read_csv(csv_path)
        for col in["Symbol", "symbol", "Ticker", "ticker"]:
            if col in df.columns:
                return sorted(df[col].dropna().astype(str).unique())
        return sorted(df.iloc[:, 0].dropna().astype(str).unique())
    except Exception:
        return []
SYMBOLS =load_symbols()
ALPHA_KEY =os.getenv("ALPHA_VANTAGE_KEY", "HQXG2RROB6JX4YLI")
FUNCTION_MAP={
    "intraday":"TIME_SERIES_INTRADAY",
    "daily":"TIME_SERIES_DAILY",
    "weekly":"TIME_SERIES_WEEKLY",
    "monthly":"TIME_SERIES_MONTHLY",
}


def get_stock_data(symbol, api_key, function_choice):
    #API function
    function=FUNCTION_MAP.get(function_choice, "TIME_SERIES_DAILY")
    params ={
        "function":function,
        "symbol":symbol,
        "apikey":api_key,
        "outputsize":"full",
    }
    if function_choice =="intraday":
        params.update({"interval":"60min"})
    url="https://www.alphavantage.co/query"
    r =requests.get(url, params=params, timeout=30)
    if r.status_code!=200:
        return None, f"HTTP error {r.status_code}"
    data =r.json()
    if not data or "Error Message" in data or "Note" in data:
        return None, data
    ts_key =None
    for k in data.keys():
        if "Time Series" in k or "TimeSeries" in k:
            ts_key =k
            break
    if not ts_key:
        return None, data
    return data[ts_key], None


def filter_and_prepare(ts_dict, start_date_str, end_date_str):
    rows=[]
    for dt_str, vals in ts_dict.items():
        try:
            dt=datetime.fromisoformat(dt_str)
        except Exception:
            try:
                dt =datetime.strptime(dt_str, "%Y-%m-%d")
            except Exception:
                continue
        rows.append((dt, vals))
    rows.sort(key=lambda r: r[0])
    try:
        start_dt =datetime.fromisoformat(start_date_str).date()
    except Exception:
        start_dt =date.min
    try:
        end_dt =datetime.fromisoformat(end_date_str).date()
    except Exception:
        end_dt=date.max
    filtered = [(dt, vals) for (dt, vals) in rows if start_dt <= dt.date() <= end_dt]
    if not filtered:
        return None
    dates =[dt.strftime("%Y-%m-%d") for dt, _ in filtered]
    open_prices =[float(vals.get("1. open") or vals.get("open")) for _, vals in filtered]
    high_prices =[float(vals.get("2. high") or vals.get("high")) for _, vals in filtered]
    low_prices=[float(vals.get("3. low") or vals.get("low")) for _, vals in filtered]
    close_prices =[float(vals.get("4. close") or vals.get("close")) for _, vals in filtered]
    return {
        "dates":dates,
        "open":open_prices,
        "high":high_prices,
        "low":low_prices,
        "close":close_prices,
    }

def make_pygal_chart(prepped, chart_type, symbol, start_date, end_date):
    if chart_type == "line":
        chart = pygal.Line(x_label_rotation=45, show_minor_x_labels=False, dots_size=2, stroke_style={"width": 2})
    else:
        chart = pygal.Bar(x_label_rotation=45, show_minor_x_labels=False)
    chart.title = f"Stock Data for {symbol}: {start_date} to {end_date}"
    chart.x_labels = prepped["dates"]
    chart.x_labels_major = prepped["dates"][::max(len(prepped["dates"])//10, 1)]
    chart.add("Open", prepped["open"]) 
    chart.add("High", prepped["high"]) 
    chart.add("Low", prepped["low"]) 
    chart.add("Close", prepped["close"]) 
    svg = chart.render()
    return svg

@app.route('/', methods=["GET", "POST"])
def index():
    chart_svg = None
    error = None
    if request.method == "POST":
        symbol = request.form.get("symbol", "").upper().strip()
        chart_type = request.form.get("chart_type", "line")
        time_series = request.form.get("time_series", "daily")
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        if not symbol:
            error = "Please select a symbol."
        else:
            ts, err = get_stock_data(symbol, ALPHA_KEY, time_series)
            if ts is None:
                error = f"Error retrieving data: {err}"
            else:
                prepped = filter_and_prepare(ts, start_date, end_date)
                if prepped is None:
                    error = "No data available for the chosen date range."
                else:
                    chart_svg = make_pygal_chart(prepped, chart_type, symbol, start_date, end_date)
    return render_template('index.html', symbols=SYMBOLS, chart_svg=chart_svg, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0')