import re
import os
import requests
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from sms_sender import AlphaSMS

load_dotenv()

input_webhook_url = os.getenv('WEBHOOK_URL', '')
API_KEY = os.getenv('ALPHASMS_API_KEY', '')
SMS_SIGNATUTE = os.getenv('SMS_SIGNATURE', '')
VIBER_SIGNATUTE = os.getenv('VIBER_SIGNATURE', '')

STAGE_ID_BOT_SALES = os.getenv('STAGE_ID_BOT_SALES', '')
STAGE_ID_DISCOUNT = os.getenv('STAGE_ID_DISCOUNT', '') 


DEF_TEXT_BOT_SALES_TO_SMS = os.getenv('SMS_TEXT_BOT_SALES', '')
DEF_TEXT_DISCOUNT_TO_SMS = os.getenv('SMS_TEXT_DISCOUNT', '')

LIST_ELEMENT_ID_WITH_TEMP = os.getenv('LIST_ELEMENT_ID_WITH_TEMP', '72')
DEAL_STAGE_ID = os.getenv('DEAL_STAGE_ID', '30')
DEAL_COLUMN_ID = None
MESSAGE_URL = None
POSTER_VIBER_IMG = None
MESSAGE_TEMPLATE = None
BTN_TEXT = None

app = Flask(__name__)
alphasms = AlphaSMS(api_key=API_KEY)


# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
fh_error = logging.FileHandler('error.log')
fh_error.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logger.addHandler(fh_error)

phone_logger = logging.getLogger('phone_logger')
fh_phone = logging.FileHandler('sent.log')
fh_phone.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
phone_logger.addHandler(fh_phone)

class MessageCache:
    def __init__(self):
        # Словник типу: { "deal_id": "stage_id" }
        self.cache = {}

    def should_send(self, deal_id=None, phone=None, stage_id=None) -> bool:
        key = str(deal_id) if deal_id else str(phone)
        last_stage = self.cache.get(key)

        if last_stage == stage_id:
            return False 

        self.cache[key] = stage_id
        return True  
    
message_cache = MessageCache()
    

# Запити до Bitrix24
def check_it_necessary_column(data, stage):
    try:
        if data:
            if data and 'result' in data and 'STAGE_ID' in data['result'] and 'result' in stage:
                
                for stage_item in stage['result']:
                    stage_name = stage_item.get('NAME', None)
                    stage_id = stage_item.get('STATUS_ID', None)
                    
                    if data['result']['STAGE_ID'].strip() == stage_id.strip():
                        return stage_id, stage_name
            
    except Exception as e:
        error_logger.error(f'Error in check_it_necessary_column: {e}')

    return False, False

def write_mess_args(data, stage_id, stage_name):
    global DEAL_COLUMN_ID, MESSAGE_URL, MESSAGE_TEMPLATE, POSTER_VIBER_IMG, BTN_TEXT

    if 'result' in data and len(data['result']) > 0:

        for item in data['result']:
            title = item['NAME'].strip()
            if title.lower() == stage_name.strip().lower():
                # DEAL_COLUMN_ID = next(iter(mess_args.get("PROPERTY_138", {}).values()), None)
                DEAL_COLUMN_ID = stage_id
                MESSAGE_URL = next(iter(item.get("PROPERTY_134", {}).values()), None)
                POSTER_VIBER_IMG = next(iter(item.get("PROPERTY_136", {}).values()), None)
                MESSAGE_TEMPLATE_OLd = next(iter(item.get("PROPERTY_132", {}).values()), None)
                BTN_TEXT = next(iter(item.get("PROPERTY_142", {}).values()), None)
                
                MESSAGE_TEMPLATE = re.sub(r'\\U([0-9A-Fa-f]{8})', lambda x: chr(int(x.group(1), 16)), MESSAGE_TEMPLATE_OLd)
                
                print("MESSAGE_TEMPLATE", MESSAGE_TEMPLATE)
                return True
            
    return False

def get_list_element_by_id(id):
    _method = 'lists.element.get.json'
    url = f'{input_webhook_url}{_method}'

    params = {
        'IBLOCK_TYPE_ID': 'lists',
        'IBLOCK_ID': id
    }

    response = requests.post(url, json=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None

def get_contact_data_by_id(id: str):
    _method = 'crm.contact.get.json'
    url = f'{input_webhook_url}{_method}'

    params = {"id": str(id)}
    try:
        response = requests.post(url, json=params)
        response.raise_for_status()  # Піднімає виключення для помилок статусу
        return response.json()
    except requests.exceptions.RequestException as e:
        error_logger.error(f'Error fetching contact data for ID {id}: {e}')
        return None

def get_contact_number_by_id(id: str):
    phone = None
    contact_data = get_contact_data_by_id(id)
    try:
        if contact_data:
            # Отримання номера телефону з даних контакту
            phone_numbers = contact_data.get('result', {}).get('PHONE', [])
            if phone_numbers and len(phone_numbers) > 0:
                phone = phone_numbers[0].get('VALUE', None)
            else:
                logging.info('Номери телефону не знайдені.')
        return phone
    except Exception as e:
        error_logger.error(f'Error in get_contact_number_by_id: {e}')
        return None

def get_deal_data_by_id(deal_id: str):
    _method = 'crm.deal.get.json'
    url = f'{input_webhook_url}{_method}'

    params = {"id": deal_id}
    try:
        response = requests.post(url, json=params)
        response.raise_for_status()  # Піднімає виключення для помилок статусу
        return response.json()
    except requests.exceptions.RequestException as e:
        error_logger.error(f'Error fetching lead data for deal ID {deal_id}: {e}')
        return None

def get_deal_category_stage_by_id(cat_id:int):
    _method = 'crm.dealcategory.stage.list'
    url = f'{input_webhook_url}{_method}'

    params = {
        "id":cat_id
    }

    response = requests.post(url, json=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None


# Оновлює змінні аргументів повідомлення за рахунок шаблону з B24
def update_mess_args(stage_id, stage_name):
    data = get_list_element_by_id(LIST_ELEMENT_ID_WITH_TEMP)
    result = write_mess_args(data, stage_id, stage_name)

    return result

def refact_phone_number(number:str):
    new_number = number
    if number:
        new_number = number.replace("(","").replace(")","").replace("-","")
    return new_number

# Вебхук запити Bitrix24
@app.route('/updateLead', methods=['POST'])
def webhook():
    try:
        data = request.form.to_dict(flat=True)
        # Перевіряємо тип події
        if 'event' in data:
            event_type = data['event']
            if event_type == 'ONCRMDEALADD' or event_type == 'ONCRMDEALUPDATE':
                deal_id = data.get('data[FIELDS][ID]', False) 
                logging.info(f'Received event {event_type} for deal ID: {deal_id}')
                if deal_id:
                    # Перевіряємо, чи це в потрібній воронці
                    deal_data = get_deal_data_by_id(deal_id)
                    dela_stage_data = get_deal_category_stage_by_id(DEAL_STAGE_ID)

                    stage_id, stage_name = check_it_necessary_column(deal_data, dela_stage_data)
                    logging.info(f'is necessary column? : {stage_name}[{stage_id}]')

                    if stage_id:
                        contact_id = deal_data.get('result', {}).get("CONTACT_ID", None)
                        logging.info(f'Contact ID: {contact_id}')
                        if contact_id:
                            result_updating = update_mess_args(stage_id, stage_name) # Оновлення аргументів повідомлення
                            if result_updating:

                                if DEAL_COLUMN_ID and MESSAGE_URL and MESSAGE_TEMPLATE and POSTER_VIBER_IMG:
                                    phone_number = get_contact_number_by_id(contact_id)
                                    phone_number = refact_phone_number(phone_number)

                                    button_text = BTN_TEXT if BTN_TEXT and BTN_TEXT.strip() else "Дізнатися більше"

                                    if not message_cache.should_send(deal_id=deal_id, stage_id=stage_id):
                                        logging.info(f'[duplication], deal_id - `{deal_id}`({phone_number}) розсилку не доставлено stage_id - `{stage_id}`')
                                        return jsonify({"status": "duplication"}), 200
                                    
                                    print(f'--- send viber message to {phone_number} with stage_id - `{stage_id}`')
                                    
                                    if stage_id == STAGE_ID_BOT_SALES:
                                        print('--- send with sms')
                                        success, result = alphasms.send_viber_mess(phone_num=phone_number, text=MESSAGE_TEMPLATE, viber_signature=VIBER_SIGNATUTE, link=MESSAGE_URL, button_txt=button_text, image=POSTER_VIBER_IMG, sms_signature=SMS_SIGNATUTE, sms_text=DEF_TEXT_BOT_SALES_TO_SMS)
                                    elif stage_id == STAGE_ID_DISCOUNT:
                                        print('--- send with sms')
                                        success, result = alphasms.send_viber_mess(phone_num=phone_number, text=MESSAGE_TEMPLATE, viber_signature=VIBER_SIGNATUTE, link=MESSAGE_URL, button_txt=button_text, image=POSTER_VIBER_IMG, sms_signature=SMS_SIGNATUTE, sms_text=DEF_TEXT_DISCOUNT_TO_SMS)

                                    else:
                                        success, result = alphasms.send_viber_mess_old(phone_num=phone_number, text=MESSAGE_TEMPLATE, viber_signature=VIBER_SIGNATUTE, link=MESSAGE_URL, button_txt=button_text, image=POSTER_VIBER_IMG)
                                    
                                    phone_logger.info(f"{phone_number} | message sending status: {success} | {result}") 
                                else:
                                    error_logger.error(f'Не оголошені дані (DEAL_COLUMN_ID={DEAL_COLUMN_ID}, MESSAGE_URL={MESSAGE_URL}, MESSAGE_TEMPLATE={MESSAGE_TEMPLATE}, POSTER_VIBER_IMG={POSTER_VIBER_IMG})')
                            else:
                                logging.info(f'Не знайдений, або не існує, елемент списку `{stage_name}` з полями для повідомлення.')
                        else:
                            logging.info('Контакт не знайдено.')
                        
                    
                else:
                    logging.warning('Не вказано ідентифікатор угоди.')
    except Exception as e:
        error_logger.error(f'Error processing webhook: {e}')
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5001'))
    app.run(host=host, port=port)
