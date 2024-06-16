from flask import Flask, jsonify
from flask import request

from main import message_router

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def return_message():
    return jsonify("working")


@app.route('/messages',methods=['POST'])
def message_handler():
    print("Request JSON:", request.get_json())
    if request.is_json:
        data = request.get_json()
        message = data.get("message","").strip()
        number = data.get("number","").strip()
        response = message_router(message.lower(),number)
        if len(response)>1:
            return jsonify({
               "response": response
            })
        else:
            return jsonify({
                "response": "enter penzi to start"
            })
    else:
        return "request must be json"


if __name__ == '__main__':
    app.run(debug=True)
