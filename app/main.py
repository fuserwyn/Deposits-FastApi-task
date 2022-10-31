from datetime import datetime
import calendar
from xml.dom import ValidationErr
from dateutil.relativedelta import relativedelta
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, validator
 
app = FastAPI()

class Deposit(BaseModel):
    date: str
    periods: int
    amount: int
    rate: float
    
    @validator('date')
    def is_str(cls, date):
        if type(date) != str:
            raise ValueError("Тип данных для date должен быть str")
        return date
    
    @validator('periods')
    def is_int_per(cls, periods):
        if type(periods) != str:
            raise ValueError("Тип данных для periods должен быть int")
        return periods

    @validator('amount')
    def is_int_amount(cls, amount):
        if type(amount) != str:
            raise ValueError("Тип данных для amount должен быть int")
        return amount
    
    @validator('rate')
    def is_float(cls, rate):
        if type(rate) != str:
            raise ValueError("Тип данных для rate должен быть float")
        return rate

class DataValidationError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

@app.exception_handler(DataValidationError)
def data_validation_exception_handler(request: Request, exc: DataValidationError):
    return JSONResponse(
        status_code = 400,
        content={'error': exc.msg}
    )

def valid_open_date(date): 
    result = True 
    try:
        valid_date = datetime.strptime(date, '%d.%m.%Y')
    except ValueError as e: 
        result = False
    finally:
        return result

def _validate_data(date, periods, amount, rate):
    if not valid_open_date(date):
        raise DataValidationError("Формат даты должен быть dd.mm.YY")
    if periods > 60 or periods < 1:
        raise DataValidationError("Количество месяцев по вкладу должно быть от 1 до 60")
    if amount <= 9999 or amount > 3000000:
        raise DataValidationError("Сумма вклада должна составлять от 10000 до 3000000") 
    if rate < 1 or rate > 8:
        raise DataValidationError("процент по вкладу должен составлять от 1 до 8")
    return 200

@app.get("/")
def root():
    return {"go_to": "http://127.0.0.1:8000/docs"}
       
@app.post("/hello")
def hello(input_json):
    try:
        parsed_json = Deposit.parse_raw(input_json)
    except ValidationError as e:
        raise DataValidationError(e.json())  
    date = parsed_json.date
    periods = parsed_json.periods
    amount = parsed_json.amount
    rate = parsed_json.rate
    status = _validate_data(date, periods, amount, rate)
    if status == 200:
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