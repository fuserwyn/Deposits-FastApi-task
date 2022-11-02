from datetime import datetime
import calendar
from xml.dom import ValidationErr
from dateutil.relativedelta import relativedelta
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, validator
 
app = FastAPI()

class DataValidationError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

def valid_open_date(date): 
    result = True 
    try:
        valid_date = datetime.strptime(date, '%d.%m.%Y')
    except ValueError as e: 
        result = False
    finally:
        return result


class Deposit(BaseModel):
    date: str
    periods: int
    amount: int
    rate: float
    
    @validator('date')
    def validate_date_type(cls, date):
        if not isinstance(date, str):
            raise TypeError("Тип данных для date должен быть str")
        return date
    
    @validator('periods', 'amount')
    def validate_integers(cls, value):
        if not isinstance(value, int):
            raise TypeError("Тип данных для periods и amount должен быть int")
        return value
    
    @validator('rate')
    def is_float(cls, rate):
        if not isinstance(rate, float):
            raise TypeError("Тип данных для rate должен быть float")
        return rate

    @validator("periods")
    def validate_periods_range(cls, periods):
        if not 1 <= periods <= 60:
            raise DataValidationError("Значение должно находиться в диапазоне от 1 до 60 включительно")
        return periods
    
    @validator("amount")
    def validate_amount_range(cls, amount):
        if amount <= 9999 or amount > 3000000:
            raise DataValidationError("Сумма вклада должна составлять от 10000 до 3000000") 
        return amount
    
    @validator("rate")
    def validate_rate_range(cls, rate):
        if rate < 1 or rate > 8:
            raise DataValidationError("процент по вкладу должен составлять от 1 до 8")
        return rate
    
    @validator("date")
    def validate_date_range(cls, date):
        if not valid_open_date(date):
            raise DataValidationError("Формат даты должен быть dd.mm.YY")
        return date

@app.exception_handler(DataValidationError)
def data_validation_exception_handler(request: Request, exc: DataValidationError):
    return JSONResponse(
        status_code = 400,
        content={'error': exc.msg}
    )

@app.get("/")
def root():
    return {"go_to": "http://127.0.0.1:8000/docs"}
       
@app.post("/hello")
def hello(input_json: Deposit):
    deposit = {
        "date": input_json.date,
        "periods": input_json.periods, 
        "amount": input_json.amount, 
        "rate": input_json.rate
    }
    date = deposit["date"]
    periods = deposit["periods"]
    amount = deposit["amount"]
    rate = deposit["rate"]
    date_deposit_open = datetime.strptime(date, "%d.%m.%Y")
    date_to_json_list = []
    amount_to_json_list = []
    curr_date = date_deposit_open
    for _ in range(periods):
        amount = amount * (1 + rate/(12 * 100))
        curr_date += relativedelta(months=1)
        curr_month_maxdays = calendar.monthrange(curr_date.year, curr_date.month)[1]
        payment_day = min(curr_month_maxdays, date_deposit_open.day)
        curr_date = curr_date.replace(day=payment_day)
        date_to_json_list.append(curr_date.strftime("%d.%m.%Y"))
        amount_to_json_list.append(round(amount, 2))
    json_dict_out = dict(zip(date_to_json_list, amount_to_json_list))
    # json_object_out = json.dumps(json_dict_out) #Если нужна json строка
    return json_dict_out