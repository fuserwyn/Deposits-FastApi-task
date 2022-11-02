import pytest
from unittest import TestCase
from urllib import response
from fastapi.testclient import TestClient
from app.main import app
from app.main import DataValidationError, valid_open_date

@pytest.mark.parametrize("data, expected_bool", 
    [({
        "date": '31.01.2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 6
    }, True), ({
        "date": '01.31.2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 6
    }, False),({
        "date": '01.31/2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 6
    }, False), ({
        "date": 'первое апреля',
        "period": 3, 
        "amount": 10000, 
        "rate": 6
    }, False)])

def test_valid_open_date(data, expected_bool):
    assert valid_open_date(data) == expected_bool

client = TestClient(app)
        
def test_main_url():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"go_to": "http://127.0.0.1:8000/docs"}

def test_main_url_bad():
    response = client.get('/oooo')
    assert response.status_code == 404

def test_post():
    deposit = {
        "date": '31.01.2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 6
    }
    response = client.post('/hello', json = deposit)
    assert response.status_code == 200
    assert response.json() == {
                        "28.02.2021": 10050,
                        "31.03.2021": 10100.25,
                        "30.04.2021": 10150.75}

def test_post_bad_calculation():
    deposit = {
        "date": '31.01.2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 6
    }
    response = client.post('/hello', json = deposit)
    assert response.status_code == 200
    assert response.json() != {
                        "28.02.2021": 100500,
                        "31.03.2021": 10100.25,
                        "30.04.2021": 10150.75}

def test_post_wrong_date():
    deposit = {
        "date": '01.31.2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 6
    }
    response = client.post('/hello', json = deposit)
    assert response.status_code == 400
    assert response.json() == {
        "error": "Формат даты должен быть dd.mm.YY"}

def test_post_wrong_period():
    deposit = {
        "date": '31.01.2021',
        "period": 61, 
        "amount": 10000, 
        "rate": 6
    }
    response = client.post('/hello', json = deposit)
    assert response.status_code == 400
    assert response.json() == {
        "error": "Количество месяцев по вкладу должно быть от 1 до 60"}

def test_post_wrong_amount():
    deposit = {
        "date": '31.01.2021',
        "period": 3, 
        "amount": 7777, 
        "rate": 6
    }
    response = client.post('/hello', json = deposit)
    assert response.status_code == 400
    assert response.json() == {
        "error": "Сумма вклада должна составлять от 10000 до 3000000"}

def test_post_wrong_rate():
    deposit = {
        "date": '31.01.2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 8.1
    }
    response = client.post('/hello', json = deposit)
    assert response.status_code == 400
    assert response.json() == {
        "error": "процент по вкладу должен составлять от 1 до 8"}