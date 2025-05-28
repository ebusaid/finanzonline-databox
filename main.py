from flask import Flask, request, jsonify
from zeep import Client
from zeep.transports import Transport
from zeep.exceptions import Fault

app = Flask(__name__)

# WSDL adresleri
SESSION_WSDL = 'https://finanzonline.bmf.gv.at/fonws/ws/sessionService.wsdl'
DATABOX_WSDL = 'https://finanzonline.bmf.gv.at/fonws/ws/databoxService.wsdl'

@app.route('/databox', methods=['POST'])
def databox_handler():
    try:
        data = request.get_json()
        tid = data.get('teilnehmerId')
        benid = data.get('benutzerId')
        pin = data.get('pin')

        if not all([tid, benid, pin]):
            return jsonify({"error": "Eksik bilgiler"}), 400

        # 1. Session başlat – HERSTELLERID eklendi
        session_client = Client(wsdl=SESSION_WSDL, transport=Transport(timeout=10))
        login_response = session_client.service.login(tid, benid, pin, "WS.TST")  # <-- BURASI GÜNCELLENDİ
        session_id = login_response.id

        # 2. DataBox verilerini al
        databox_client = Client(wsdl=DATABOX_WSDL, transport=Transport(timeout=10))
        databox_response = databox_client.service.getDatabox(
            tid, benid, session_id, '', None, None
        )

        return jsonify({
            "session_id": session_id,
            "databox_result": databox_response
        })

    except Fault as fault:
        return jsonify({"error": f"SOAP hatası: {str(fault)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Beklenmeyen hata: {str(e)}"}), 500

# Flask sunucusunu başlat
app.run(host='0.0.0.0', port=8000)
