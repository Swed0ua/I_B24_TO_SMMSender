import requests


webhook_url = 'https://smartkasa.bitrix24.eu/rest/9306/2t1phn72pwwh3t3p/'

def get_list_element_by_id(id):
    _method = 'lists.element.get.json'
    url = f'{webhook_url}{_method}'

    params = {
        'IBLOCK_TYPE_ID': 'lists',
        'IBLOCK_ID': id
    }

    response = requests.post(url, json=params)
    print(response.text)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None

def get_contact_data_by_id(id:int):
    _method = 'crm.contact.get.json'
    url = f'{webhook_url}{_method}'

    params = {
        "id":id
    }

    response = requests.post(url, json=params)
    print(response.text)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None

def get_dead_data_by_id(deal_id:int):
    _method = 'crm.deal.get.json'
    url = f'{webhook_url}{_method}'

    params = {
        "id":deal_id
    }

    response = requests.post(url, json=params)

    print(response.text)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None

def get_dead_category_data_by_id(cat_id:int):
    _method = 'crm.deal.get.json'
    url = f'{webhook_url}{_method}'

    params = {
        "id":cat_id
    }

    response = requests.post(url, json=params)

    print(response.text)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None


def check_it_necessary_column(data, column_id:str="C22:UC_TULWHN"):
    if data:
        try:
            return data['result']['STAGE_ID'].strip() == column_id.strip()
        except:
            pass
    return False
        
data = get_list_element_by_id("72")
