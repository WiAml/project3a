from datetime import datetime
#user inputs chart type
def get_chart_type():
    chart_type =input("Enter chart type (line/bar): ").lower().strip()
    while chart_type not in ["line", "bar"]:
        print("Error: Please enter 'line' or 'bar'.")
        chart_type =input("Enter chart type (line/bar): ").lower().strip()
    return chart_type
#user selects time series
def get_time_series_function():
    while True:
        print("Select time series:")
        print("1 = Intraday")
        print("2 = Daily")
        print("3 = Weekly")
        print("4 = Monthly")
        choice =input("Enter 1, 2, 3, or 4: ").strip()
        mapping ={
            "1": "intraday",
            "2": "daily",
            "3": "weekly",
            "4": "monthly"}
        if choice in mapping:
            return mapping[choice]
        else:
            print("Invalid choice. Please try again.")
#user inputs start and end dates respectivly
def get_start_date():
    while True:
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            return start_date
        except ValueError:
            print("Invalid date. Please enter in YYYY-MM-DD format.")
def get_end_date():
    while True:
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
            return end_date
        except ValueError:
            print("Invalid date. Please enter in YYYY-MM-DD format.")
#user selects stock symbol
def get_symbol():
    symbol = input("Enter stock symbol: ").upper().strip()
    while not symbol.isalpha():
        print("Invalid symbol. It must contain only letters.")
        symbol = input("Enter stock symbol: ").upper().strip()
    return symbol