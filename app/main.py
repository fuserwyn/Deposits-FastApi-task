from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta
import json
from fastapi import FastAPI, Body
from fastapi.responses import FileResponse
 
app = FastAPI()

class Deposit:
    def __init__(self, date, amount):
        self.date = date
        self.amount = amount

@app.get("/")
def root():
    return FileResponse("public/index.html")
# def hello(json_str):
    #json_dict=json.loads(json_str)
@app.post("/hello")
def hello(date: str  = Body(...,embed=True), 
            period: int = Body(...,embed=True),
            amount: int = Body(...,embed=True),
            rate: float = Body(...,embed=True)):
    json_dict = {
        "date": date,
        "period": period, 
        "amount": amount, 
        "rate": rate
    }
    
    # date = json_dict["date"]
    # period = json_dict["period"]
    # amount = json_dict["amount"]
    # rate = json_dict["rate"]
    
    # Serializing json  
    # json_object = json.dumps(json_dict)
    
    date_deposit_open = datetime.strptime(date, "%d.%m.%Y")
    
    date_to_json_list = []
    amount_to_json_list = []
    curr_date = date_deposit_open
    for _ in range(period):
        amount = amount * (1 + rate/(12 * 100))
        curr_date += relativedelta(months=1)
        curr_month_maxdays = calendar.monthrange(curr_date.year, curr_date.month)[1]
        payment_day = min(curr_month_maxdays, date_deposit_open.day)
        curr_date = curr_date.replace(day=payment_day)
        print(curr_date)
        date_to_json_list.append(curr_date.strftime("%d.%m.%Y"))
        amount_to_json_list.append(round(amount, 2))
    json_dict_out = dict(zip(date_to_json_list, amount_to_json_list))
    json_object_out = json.dumps(json_dict_out) 
    print(json_object_out)

    return json_object_out