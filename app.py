from flask import Flask, jsonify, render_template
import requests
from lxml import etree
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

# Helper function to fetch data from Ministry of Sports
def fetch_sports_data():
    try:
        url = "https://opendata.mos.gov.sa/api.asmx?WSDL"
        headers = {"Content-Type": "text/xml; charset=utf-8"}
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                   xmlns:mos="http://api.mos.gov.sa/">
                   <soapenv:Header/>
                   <soapenv:Body>
                      <mos:GetPlayersStatistics/>
                   </soapenv:Body>
                </soapenv:Envelope>"""

        response = requests.post(url, data=body, headers=headers, verify=False)
        response.raise_for_status()

        # Parse the response using lxml
        root = etree.fromstring(response.content)
        data = []

        for element in root.findall(".//Get_ATHLETES"):
            club_name = element.find("CLUBNAME").text
            players_count = int(element.find("PLAYERSCOUNT").text)
            data.append({"club": club_name, "playersCount": players_count})

        return data
    except Exception as e:
        return {"error": str(e)}


@app.route('/api/analysis', methods=['GET'])
def analysis():
    try:
        data = fetch_sports_data()
        if "error" in data:
            return jsonify({"error": data["error"]})

        # Sort clubs by player count
        sorted_clubs = sorted(data, key=lambda x: x["playersCount"], reverse=True)
        top_clubs = sorted_clubs[:5]

        # Add a custom message for Al Hilal
        message = "هل هذا معناته أن النادي الأفضل هو اللي عنده لاعبين أكثر؟ إذا كان الهلال فهو educated guess والإجابة ايه، غيره ما اعتقد."

        return jsonify({"topClubs": top_clubs, "allClubs": sorted_clubs, "message": message})
    except Exception as e:
        return jsonify({"error": str(e)})



# Serve the front-end visualization
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
