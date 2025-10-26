from flask import Flask, request, jsonify

# C22:UC_TULWHN для колонки "Думає отримав презентацію"

app = Flask(__name__)
webhook_url = 'https://smartkasa.bitrix24.eu/rest/9306/7brcqjy7xef7f69j/'

def get_info_about_lead(id):
    _method = 'crm.deal.add.json'
    url = f'{webhook_url}{_method}'

# Обробка вебхука
@app.route('/updateLead', methods=['POST'])
def webhook():
    data = request.form.to_dict(flat=True) 
    # Перевіряємо тип події
    if 'event' in data:
        event_type = data['event']
        if event_type == 'onCrmDealAdd' or event_type == 'onCrmDealUpdate':
            deal_id = data.get('data[FIELDS][ID]', False) # індитифікатор угоди
            print('deal_id', deal_id)
            if deal_id:
                pass
                # Перевіряємо чи це в потрібній воронці
            

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
