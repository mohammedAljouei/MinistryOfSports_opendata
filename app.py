from flask import Flask, jsonify, request
import requests
from lxml import etree

app = Flask(__name__)

# SOAP API 
SOAP_URL = "https://opendata.mos.gov.sa/api.asmx"
HEADERS = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "http://api.mos.gov.sa/GetPlayersStatistics"
}
SOAP_REQUEST = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetPlayersStatistics xmlns="http://api.mos.gov.sa/" />
  </soap:Body>
</soap:Envelope>
"""

@app.route('/analyze', methods=['GET'])
def analyze():
    try:
        # Send SOAP request
        response = requests.post(SOAP_URL, data=SOAP_REQUEST, headers=HEADERS, verify=False)

        # Parse XML response
        root = etree.fromstring(response.content)
        namespaces = {'ns': 'http://api.mos.gov.sa/'}
        players = root.xpath("//Get_ATHLETES", namespaces=namespaces)

        # Extract data into a list of dictionaries
        results = []
        for player in players:
            club_name = player.find("CLUBNAME").text
            players_count = int(player.find("PLAYERSCOUNT").text)
            results.append({"club_name": club_name, "players_count": players_count})

        # Top 5 clubs by player count
        top_clubs = sorted(results, key=lambda x: x["players_count"], reverse=True)[:5]
        print(top_clubs)

        return jsonify({"top_clubs": top_clubs, "total_clubs": len(results)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
