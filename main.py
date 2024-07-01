from db import mydb, check_if_user_exists, insert_initial_message, create_user, insert_message, add_user_details, \
    record_description, fetch_match_count, insert_match, get_matches, fetch_gender, fetch_next_matches, \
    fetch_next_occurrences, fetch_user_details, fetch_description, get_requestor_number, check_for_requestor, \
    fetch_time_and_message_sent
from flask import json
from datetime import datetime
import requests
kenyan_counties = [
        "mombasa",
        "kwale",
        "kilifi",
        "tana river",
        "lamu",
        "taita-taveta",
        "garissa",
        "wajir",
        "mandera",
        "marsabit",
        "isiolo",
        "meru",
        "tharaka-nithi",
        "embu",
        "kitui",
        "machakos",
        "makueni",
        "nyandarua",
        "nyeri",
        "kirinyaga",
        "murang'a",
        "kiambu",
        "turkana",
        "west pokot",
        "samburu",
        "trans-nzoia",
        "uasin gishu",
        "elgeyo-marakwet",
        "nandi",
        "baringo",
        "laikipia",
        "nakuru",
        "narok",
        "kajiado",
        "kericho",
        "bomet",
        "kakamega",
        "vihiga",
        "bungoma",
        "busia",
        "siaya",
        "kisumu",
        "homa bay",
        "migori",
        "kisii",
        "nyamira",
        "nairobi"
    ]
matches_result = None
def validate_registration(message):


    msg_array = message.split('#')
    if " " not in msg_array[1]:
        return False,"please enter first and last name as in the example given"
    if len(msg_array) != 6:
        response = "please enter all details"
        return False,response
    try:
        int(msg_array[2])
    except ValueError:
        return False,"please enter a valid age"
    if msg_array[3] not in ["male","female"]:
        response = "please enter valid gender"
        return False,response
    if msg_array[4] not in kenyan_counties:
        return False,"please enter a valid county"
    return True,"valid"
def validate_details(message):
    msg_array = message.split('#')
    if len(msg_array) != 6:
        return False,"please enter all details"
    if msg_array[1] not in ["diploma","certificate","degree","masters","phd"]:
        return False,"please enter a valid level of education"
    if msg_array[3] not in ["single","divorced","widow","widower","widowed"]:
        return False,"please enter a valid marital status"
    return True,"valid"

def number_checker(number):
    if number.startswith("254") and len(number.replace("254","0"))==10:
        return True,number.replace("254","0")
    if len(number)==10 and "07" or "01" in number:
        return True,number
    return False,"number not valid"
def send_first_message(number):
    response = """Welcome to our dating service with 6000 potential dating partners!
            To register SMS start#name#age#gender#county#town to 22141.
            E.g., start#John Doe#26#Male#Nakuru#Naivasha"""
    insert_initial_message(number, response)
    return response

def create_profile(number,message):
    activator, name, age, gender, county, city = message.split('#')
    create_user(number, name, age, gender, county, city)
    response = f"""Your profile has been created successfully {name}.
    SMS details#levelOfEducation#profession#maritalStatus#religion#ethnicity to 
    22141.
    E.g. details#diploma#driver#single#christian#mijikenda"""
    insert_message(sender="22141", receiver=number, message=response)
    return response

def update_profile(number,message):
    activator, level_of_education, profession, marital_status, religion, ethnicity = message.split('#')
    add_user_details(number, level_of_education, profession, marital_status, religion, ethnicity)
    response = """This is the last stage of registration.
    SMS a brief description of yourself to 22141 starting with the word MYSELF.
    E.g., MYSELF chocolate, lovely, sexy etc"""
    insert_message(sender="22141", receiver=number, message=response)
    return response

def update_description(number,message):
    record_description(number,message)
    response = """You are now registered for dating.
To search for a MPENZI, SMS match#age#town to 22141 and meet the person of 
your dreams.
E.g., match#23-25#Kisumu"""
    return response

def get_number_of_matches(message,gender):
    results = fetch_match_count(message,gender)
    if len(results) == 0:
        response = "No matches found for your request."
        return response,[]
    else:
        response = f"""We have {len(results)} {"ladies" if gender.strip()=="male"else"men"} who match your choice! We will send you details of them 
shortly.
To get more details about a {"lady" if gender.strip()=="male"else"male"}, SMS {"his" if gender.strip()=="male"else"her"} number e.g., 0722010203 to 22141"""
        return response,results

def store_results(results):
    return results
def send_first_three(results):
    matches = []
    if len(results) == 1 or len(results) == 2:
        for result in results:
            result_info = f"{result[0]} aged {result[1]}, {result[2]}"
            matches.append(result_info)
        response = f"""{matches[0]} {matches[1] if len(matches)==2else ""}"""
        return response
    if len(results) >= 3:
        first_three = results[:3]
        for match in first_three:
            match_info = f"{match[0]} aged {match[1]}, {match[2]}"
            matches.append(match_info)
        response = f"""{matches[0]}
         {matches[1]} {matches[2]} Send NEXT to 22141 to receive details of the remaining {len(results)-3} matches"""
        # time.sleep(5)
        return response
def get_next_matches(results,page):
    page_times_three = page*3
    results_length = len(results)-3
    difference = results_length - page_times_three
    if page_times_three>results_length:
        return "no more matches"
    if len(results)<6:
        next_three = results[3:]
        matches = []
        for match in next_three:
            match_info = f"{match[0]} aged {match[1]}, {match[2]}"
            matches.append(match_info)
        response = f"""{matches[0]}
                        {matches[1]} 
                        {matches[2]}"""
        return response
    if len(results)>=6 and page_times_three<=results_length:
        start_point = page*3
        end_point = start_point+3
        next_three = results[start_point:end_point]
        matches = []
        for match in next_three:
            match_info = f"{match[0]} aged {match[1]}, {match[2]}"
            matches.append(match_info)
        response = f"""{matches[0]}\n{matches[1]}\n{matches[2]}"""
        return response

def get_access_token():
    session = requests.session()
    session.headers.update({'Content-Type': 'application/json',
                            'Authorization': 'Basic REVBYjhjb3FBejZxYUV5N3FDS1Z6U2ZOWUViRkozQXRtYTE3TThmeW10VUM2T0dHOmNXR0pES0JHdnRnWVZER3RDd0R6a2JxOVhWQTR5YU16Qk9mMmVBMDhSV3N0Vm5OTjJHejFpb0FrSTlrTUdvcUE='})
    get_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = session.get(get_url)
    insert_message(sender="safaricom",receiver="22141",message=response.json().get('access_token'))
    return response
def send_payment_request(number):
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    data = {
    "BusinessShortCode": 174379,
    "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwNjIxMTEzNDMx",
    "Timestamp": "20240621113431",
    "TransactionType": "CustomerPayBillOnline",
    "Amount": 50,
    "PartyA": 254705832092,
    "PartyB": 174379,
    "PhoneNumber": 254705832092,
    "CallBackURL": "https://saf-response.onrender.com/response",
    "AccountReference": "Matchrequest",
    "TransactionDesc": "Payment of X"
  }
    timeSent = fetch_time_and_message_sent()
    elapsed_time = timeSent[0][0] - datetime.now()
    if len(timeSent)>0 and elapsed_time.seconds < 3599 and elapsed_time.days == 0:
        insert_message(sender="22141",receiver=number,message="payment request for penzi match")
        session = requests.session()
        session.headers.update({'Content-Type': 'application/json',
                                'Authorization': f'Bearer {timeSent[0][1]}'})
        response = session.post(url, json=data)
        return response
    else:
        response_body = get_access_token()
        insert_message(sender="22141", receiver=number, message="payment request for penzi match")
        session = requests.session()
        session.headers.update({'Content-Type': 'application/json',
                                'Authorization': f'Bearer {response_body.get("access_token")}'})
        response = session.post(url, json=data)
        return response


# def get_payment_status():
#     session = requests.session()
#     response = session.get("https://isaacngahu.pythonanywhere.com")
#     return response.json()



def message_router(message,number):
    number_is_valid,valid_number=number_checker(number)
    user_details = fetch_user_details(valid_number)
    has_requestor,requestor_details = check_for_requestor(valid_number)
    user_exists = check_if_user_exists(valid_number)
    if message == "penzi" and not user_exists and number_is_valid:
        response = send_first_message(valid_number)
        return response
    if len(message.split("#"))==6 and not user_exists and"start" and "#" in message  and number_is_valid:
        is_valid,response = validate_registration(message)
        if is_valid:
            response = create_profile(valid_number,message)
            return response
        else:
            return response
    # if user_exists is None:
    #     return "please register first"
    if '#' in message and message.split('#')[0]=="details":
        is_valid,response = validate_details(message)
        if is_valid:
            response = update_profile(valid_number,message)
            return response
        else:
            return response
    if "myself" in message:
        response = update_description(valid_number,message)
        return response
    if "#" in message and "match" in message and user_exists and len(message.split('#')) == 3 and '-' in message.split('#')[1] and message.split('#')[2] in kenyan_counties:
        response = send_payment_request(valid_number)
        confirmation = response.json()
        if confirmation.get("ResponseDescription","").strip() == "Success. Request accepted for processing":
            insert_message(sender=valid_number, receiver="22141", message=message)
            insert_match(user_number=valid_number, request=message, page_number=1)
            gender = fetch_gender(valid_number)
            resp1, results = get_number_of_matches(message, gender[0])
            if len(results) > 0:
                resp2 = send_first_three(results)
                return resp1 + " " + resp2
            return resp1
        return "check your network connection and send your match request again"
    if message=="next" and user_exists and number_is_valid:
        insert_message(sender=valid_number,receiver="222141",message=message)
        gender = fetch_gender(valid_number)
        results, page = fetch_next_matches(valid_number, gender)
        matches = get_next_matches(results, page)
        insert_message(sender="22141",receiver=valid_number,message=matches)
        if not matches == "no more matches":
            next_occurrences = fetch_next_occurrences(valid_number)
            next_occurrences_counter = len(next_occurrences) + 1
            insert_match(user_number=valid_number,request=matches,page_number= 2 if len(next_occurrences)==1 else next_occurrences_counter )
        return matches
    if "describe" in message and user_exists and ("07" in message or "01" in message):
        insert_message(sender=valid_number,receiver="22141",message=message)
        requested_number = message.replace("describe","").strip()
        name_and_description = fetch_description(requested_number)
        if len(name_and_description)==1:
            name,description = name_and_description[0]
            response = f"""{name} describes themselves as {description}"""
            return response
        else:
            return "user not found"
    if len(message)==10 and user_exists and number_is_valid and ("07" in message or "01" in message):
        insert_message(sender=valid_number,receiver="22141",message=message)
        user_details = fetch_user_details(message)
        if len(user_details)==1 and len(user_details[0])==11:
            number, name, age, gender, county, city, level_of_education, profession, marital_status, ethnicity, religion = user_details[0]
            response = f"""{name} aged {age}, {county} county, {city} town, {level_of_education}, {profession}, {marital_status}, {ethnicity}, {religion}.  Send DESCRIBE {number} to get more details."""
            requestor_details = fetch_user_details(valid_number)
            if len(requestor_details[0])==11:
                requestor_number, requestor_name, requestor_age, requestor_gender, requestor_county, requestor_city, requestor_level_of_education, requestor_profession, requestor_marital_status, requestor_ethnicity, requestor_religion = requestor_details[0]
                inform_requested_message = f"""Hi {name} a {"man" if requestor_gender == "male" else "lady"}  is interested in you and requested your details.
                                    {"He" if requestor_gender == "male" else "She"} is aged {requestor_age} based in {requestor_county}.
                                    Do you want to know more about {"him" if requestor_gender == "male" else "her"}? Send YES to 22141"""
                if len(user_details) == 11 and len(requestor_details) == 11:
                    insert_message(sender="22141", receiver=valid_number, message=response)
                    insert_message(sender="22141", receiver=number, message=inform_requested_message)
                return response
        return "user was not found"
    if has_requestor and len(requestor_details)==0:
        requestor_name,requestor_age,requestor_county = requestor_details[0]
        user_details = fetch_user_details(valid_number)
        response = f"""Hi {user_details[0][1]}, {requestor_name} is interested in you and requested your details.
 aged {requestor_age} based in {requestor_county}.
Do you want to know more? Send YES to 22141"""
        insert_message(sender="22141", receiver=valid_number, message=response)
        return response
    if message=="yes" and has_requestor:
        insert_message(sender=valid_number,receiver="22141",message=message)
        requestor_number = get_requestor_number(valid_number)
        user_details = fetch_user_details(requestor_number)
        number,name,age,gender,county,city,level_of_education,profession,marital_status,ethnicity,religion = user_details[0]
        response = f"""{name} aged {age}, {county} county, {city} town, {level_of_education}, {profession}, {marital_status}, {ethnicity}, {religion}.  Send DESCRIBE {number} to get more details."""
        return response
    if user_exists and len(user_details)==1 and len(user_details[0][1])>1 and user_details[0][6] is None:
        response = """You were registered for dating with your initial details.
To search for a MPENZI, SMS match#age#town to 22141 and meet the person of 
your dreams.
E.g., match#23-25#Nairobi"""
        insert_message(sender="22141", receiver=valid_number, message=response)
        return response
    return "please check if the number or the message you have entered is in the correct format"

# print(get_number_of_matches("match#23-25#nairobi","female"))
# print(get_next_matches("0725467800","male"))
# print(number_checker("0725635435"))
def get_difference():
    time_ = [(datetime.datetime(2024, 6, 28, 11, 14, 31),)]
    # time_sent = datetime.strptime(time_[0][0],'%Y-%m-%d %H:%M:%S')
    return datetime.datetime.now() - time_[0][0]

#print(get_payment_status())


