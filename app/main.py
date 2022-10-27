from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
 
app = FastAPI()

class Deposit(BaseModel):
    date: str
    period: int
    amount: int
    rate: float

class DataValidationError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

@app.exception_handler(DataValidationError)
def data_validation_exception_handler(request: Request, exc: DataValidationError):
    return JSONResponse(
        status_code = 400,
        content={'error': exc.msg}
    )

def valid_open_date(json_dict): 
    result = True 
    try:
        valid_date = datetime.strptime(json_dict["date"], '%d.%m.%Y')
    except ValueError as e: 
        result = False
    finally:
        return result

def _validate_data(json_dict):
    if not valid_open_date(json_dict):
        raise DataValidationError("Формат даты должен быть dd.mm.YY")
    if json_dict["period"] > 60 or json_dict["period"] < 1:
        raise DataValidationError("Количество месяцев по вкладу должно быть от 1 до 60")
    if json_dict["amount"] <= 9999 or json_dict["amount"] > 3000000:
        raise DataValidationError("Сумма вклада должна составлять от 10000 до 3000000")
    if json_dict["rate"] < 1 or json_dict["rate"] > 8:
        raise DataValidationError("процент по вкладу должен составлять от 1 до 8")
    return 200

@app.get("/")
def root():
    return {"go_to": "http://127.0.0.1:8000/docs"}
       
@app.post("/hello")
def hello(deposit: Deposit):
    json_dict = {
        "date": deposit.date,
        "period": deposit.period, 
        "amount": deposit.amount, 
        "rate": deposit.rate
    }
    status = _validate_data(json_dict)
    if status == 200:
        date = json_dict["date"]
        period = json_dict["period"]
        amount = json_dict["amount"]
        rate = json_dict["rate"]
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
            date_to_json_list.append(curr_date.strftime("%d.%m.%Y"))
            amount_to_json_list.append(round(amount, 2))
        json_dict_out = dict(zip(date_to_json_list, amount_to_json_list))
        json_object_out = json.dumps(json_dict_out) #Если нужна json строка
    return json_dict_out  