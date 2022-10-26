from unittest import TestCase
from urllib import response
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app as web_app

class APITestCase(TestCase):
    
    def setUp(self):
        self.client = TestClient(web_app)
        
    def test_main_url(self):
        response = self.client.post('/')
        self.assertEqual(response.status_code, 200)
        
    # def test_valid_data(self):
        # data = {
        #     'data':{
        #         "date": 'date',
        #         "period": 'period', 
        #         "amount": 'amount', 
        #         "rate": 'rate'
        #     }
        # }
        # response = self.client.post('/data', json=data)
        # self.assertEqual(response.status_code, 200)
    # get_date = lambda d: datetime.strptime(d, '%d.%m.%Y').date() <= datetime.today().date()
    #     assert get_date('14.09.2019')  # OK
    #     assert get_date('15.09.2019')  # AssertionError
    #     assert get_date('32.09.2019')  # ValueError: time data '32.09.2019' does not match format '%d.%m.%Y'