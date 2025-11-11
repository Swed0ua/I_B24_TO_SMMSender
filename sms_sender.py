import random
import requests
import json
from typing import Optional, Tuple, List, Dict
from datetime import datetime

class AlphaSMS:
    def __init__(self, api_key: str, url: str = 'https://alphasms.ua/api/json.php'):
        self.api_key = api_key
        self.url = url
        self.base_url = "https://alphasms.ua/api/http.php"
        self.headers = {
            'Content-Type': 'application/json',
            'Encoding': 'UTF-8'
        }

    def _make_request(self, payload: List[Dict]) -> Optional[dict]:
        """ Відправляє запит до AlphaSMS і повертає результат.
            * Відправляти payload списком list[]
        """
        try:
            data =  {
                "auth": self.api_key,
                "data": payload
            }

            response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
            response.raise_for_status()  # Викликатиме помилку при невдалому статусі
            return response.json()
        except requests.RequestException as e:
            print(f"HTTP Помилка: {e}")
            return None

    def get_balance(self) -> Tuple[bool, Optional[str]]:
        """
        Запитує баланс на AlphaSMS.
        
        Повертає кортеж (успіх, повідомлення або баланс).
        """
        payload = {
            "type": "balance"
        }

        response_data = self._make_request([payload])
        
        if response_data is None:
            return False, "Не вдалося з'єднатися з сервером"

        if response_data.get('success'):
            try:
                balance_info = response_data['data'][0]['data']
                amount = balance_info['amount']
                currency = balance_info['currency']
                return True, f"Баланс: {amount} {currency}"
            except (KeyError, IndexError):
                return False, "Не вдалося отримати баланс"
        else:
            return False, response_data.get('error', 'Невідома помилка')

    def send_sms(self, phone_num:int, text:str, title:str) -> Tuple[bool, Optional[str]]:
        """
        Відправляє смс через AlphaSMS.
        """
        new_id = datetime.now().strftime("%Y%m%d%H%M%S")
        payload = {
            "type": "sms",
            "id": new_id,
            "phone": phone_num,
            "sms_signature": title,
            "sms_message": text
        }       

        response_data = self._make_request([payload])
        print('response_data', response_data)
        if response_data is None:
            return False, "Не вдалося з'єднатися з сервером"

        if response_data.get('success'):
            try:
                balance_info = response_data['data'][0]['data']
                id = balance_info['id']
                msg_id = balance_info['msg_id']
                return True, f"Смс відправлено: id:{id} msg_id:{msg_id}"
            except (KeyError, IndexError):
                return False, "Не відправити смс"
        else:
            return False, response_data.get('error', 'Невідома помилка')

    def send_viber_mess_old(self, phone_num:int, text:str, viber_signature:str, link:str, button_txt:str, image:str) -> Tuple[bool, Optional[str]]:
        """
        Відправляє смс через AlphaSMS.
        """

        text = text.replace("\\n", "\n")

        new_id = datetime.now().strftime("%Y%m%d%H%M%S%f") + str(random.randint(1000, 9999))
        payload = {
            "type": "viber",
            "id": new_id,
            "phone": phone_num,
            "viber_type": "text+image+link",
            "viber_signature": viber_signature,
            "viber_message": text,
            "viber_image": image,
            "viber_link": link,
            "viber_button": button_txt,
        
        }     

        response_data = self._make_request([payload])
        print('response_data', response_data)
        if response_data is None:
            return False, "Не вдалося з'єднатися з сервером"

        if response_data.get('success'):
            try:
                balance_info = response_data['data'][0]['data']
                print('res', balance_info)
                id = balance_info['id']
                msg_id = balance_info['msg_id']
                return True, f"Viber повідомлення відправлено: id:{id} msg_id:{msg_id}"
            except (KeyError, IndexError):
                return False, "Не відправити Viber повідомлення"
        else:
            return False, response_data.get('error', 'Невідома помилка')

    def send_viber_mess(self, phone_num:int, text:str, viber_signature:str, link:str, button_txt:str, image:str, sms_signature:str, sms_text:str) -> Tuple[bool, Optional[str]]:
        """
        Відправляє смс через AlphaSMS.
        """

        text = text.replace("\\n", "\n")
        sms_text = sms_text.replace("\\n", "\n")
        
        new_id = datetime.now().strftime("%Y%m%d%H%M%S%f") + str(random.randint(1000, 9999))
        payload = {
            "type": "viber+sms",
            "id": new_id,
            "phone": phone_num,
            "sms_signature": sms_signature,
            "sms_message": sms_text,
            "viber_type": "text+image+link",
            "viber_signature": viber_signature,
            "viber_message": text,
            "viber_image": image,
            "viber_link": link,
            "viber_button": button_txt,
            "short_link": False
        }     

        response_data = self._make_request([payload])
        print('response_data', response_data)
        if response_data is None:
            return False, "Не вдалося з'єднатися з сервером"

        if response_data.get('success'):
            try:
                balance_info = response_data['data'][0]['data']
                print('res', balance_info)
                id = balance_info['id']
                msg_id = balance_info['msg_id']
                return True, f"Viber повідомлення відправлено: id:{id} msg_id:{msg_id}"
            except (KeyError, IndexError):
                return False, "Не відправити Viber повідомлення"
        else:
            return False, response_data.get('error', 'Невідома помилка')

