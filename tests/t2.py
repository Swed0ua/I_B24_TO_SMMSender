import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
webhook_url = os.getenv('WEBHOOK_URL', '')

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
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5001'))
    app.run(host=host, port=port)
