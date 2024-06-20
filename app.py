from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

from db import fetch_user_details, insert_message, check_for_requestor
from main import message_router, number_checker

app = Flask(__name__)
app.config['DEBUG'] = True
CORS(app)


def check_user_progress(number):
    user_details = fetch_user_details(number)
    has_requestor,requestor_details = check_for_requestor(number)
    if len(user_details) == 1 and len(user_details[0][1]) > 1 and user_details[0][6] is None:
        response = """You were registered for dating with your initial details.
    To search for a MPENZI, SMS match#age#town to 22141 and meet the person of 
    your dreams.
    E.g., match#23-25#Nairobi"""
        insert_message(sender="22141", receiver=number, message=response)
        return response
    if has_requestor and len(requestor_details) == 0:
        requestor_name, requestor_age, requestor_county = requestor_details[0]
        user_details = fetch_user_details(number)
        response = f"""Hi {user_details[0][1]}, {requestor_name} is interested in you and requested your details.
 aged {requestor_age} based in {requestor_county}.
Do you want to know more? Send YES to 22141"""
        insert_message(sender="22141", receiver=number, message=response)
        return response
    return "no updates"



@app.route('/messages/<string:number>', methods=['GET'])
def return_message(number):
    try:
        is_valid, valid_number = number_checker(number)
        if is_valid and request.is_json:
            response = check_user_progress(valid_number)
            print(response)
            return jsonify({"update": response})
    except Exception as e:
        return jsonify({"update": str(e)})



@app.route('/messages',methods=['POST'])
def message_handler():
    print("Request JSON:", request.get_json())
    if request.is_json:
        data = request.get_json()
        message = data.get("message","").strip()
        number = data.get("number","").strip()
        response = message_router(message.lower(),number)
        print(response)
        if len(response)>1:
            return jsonify({
               "response": response
            })
        else:
            return jsonify({
                "response": "enter penzi to start"
            })



if __name__ == '__main__':
    app.run(debug=True)
