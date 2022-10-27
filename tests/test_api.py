import pytest
from unittest import TestCase
from urllib import response
from fastapi.testclient import TestClient
from app.main import app as web_app
from app.main import DataValidationError, _validate_data, valid_open_date

class APITestCase(TestCase):
    
    def setUp(self):
        self.client = TestClient(web_app)
        
    def test_main_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
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
    }, False) ])

def test_valid_data(data, expected_bool):
    assert valid_open_date(data) == expected_bool

@pytest.mark.parametrize("expected_exception, data",
    [(DataValidationError,{
        "date": '31.01.2021',
        "period": 0, 
        "amount": 10000, 
        "rate": 6
    }), (DataValidationError,{
        "date": '31.01.2021',
        "period": 3, 
        "amount": 9999, 
        "rate": 6
    }),(DataValidationError,{
        "date": '31.01.2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 9
    }),(TypeError,{
        "date": '31.01.2021',
        "period": '3', 
        "amount": 10000, 
        "rate": 6
    }),(TypeError,{
        "date": '31.01.2021',
        "period": 3, 
        "amount": '10000', 
        "rate": 6
    })] )

def test_valid_period_or_amount_or_rate_negative(expected_exception, data):
    with pytest.raises(expected_exception):
        _validate_data(data)

@pytest.mark.parametrize("data, expected_result",[({
        "date": '31.01.2021',
        "period": 3, 
        "amount": 10000, 
        "rate": 6
    }, 200), ({
        "date": '31.12.2022',
        "period": 60, 
        "amount": 3000000, 
        "rate": 8
    }, 200),({
        "date": '19.03.2000',
        "period": 30, 
        "amount": 100000, 
        "rate": 7.99
    }, 200)
    ])

def test_valid_period_or_amount_or_rate_positive(data, expected_result):
    assert _validate_data(data) == expected_result
