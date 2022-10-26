from datetime import datetime
import calendar
from distutils.log import error
from email import header
from dateutil.relativedelta import relativedelta
import json
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
 
app = FastAPI()

# class Dummy(BaseModel):
#     name: str

# class HTTPError(BaseModel):
#     detail: str

#     class Config:
#         schema_extra = {
#             "example": {"error": "Описание ошибка"},
#         }
      
def valid_open_date(json_dict): 
    result = True 
    try:
        valid_date = datetime.strptime(json_dict["date"], '%m.%d.%Y')
    except ValueError as e: 
        result = False
    finally:
        return result
    
# @app.get(
#     "/test",
#     responses={
#         200: {"model": Dummy},
#         409: {
#             "model": HTTPError,
#             "description": "This endpoint always raises an error",
#         },
#     },
# )



def _validate_data(json_dict):
    if not valid_open_date(json_dict):
        raise HTTPException(400, detail={"error": "Описание ошибка"})
    elif json_dict["period"] > 60 or json_dict["period"] < 1:
        status = 400
    elif json_dict["amount"] <= 9999 or json_dict["amount"] > 3000000:
        status = 400
    elif json_dict["rate"] < 1 or json_dict["rate"] > 8:
        status = 400
    else:
        status = 200
    print(status)
    return status
        
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
    status = _validate_data(json_dict)
    if status == 200:
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
        json_object_out = json.dumps(json_dict_out) #Если нужна json строка
    else:
       raise HTTPException(400, detail={"error": "Описание ошибка"})
    return json_dict_out  
        