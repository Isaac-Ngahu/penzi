from db import mydb, check_if_user_exists, insert_initial_message, create_user, insert_message, add_user_details, \
    record_description, fetch_match_count, insert_match, get_matches, fetch_gender, fetch_next_matches, \
    fetch_next_occurrences, fetch_user_details, fetch_description
import threading
import time
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
        return False,"please enter first and last name"
    if len(msg_array) != 6:
        response = "please enter all details"
        return False,response
    try:
        int(msg_array[2])
    except ValueError:
        return False,"please enter a valid age"
    if msg_array[4] not in kenyan_counties:
        return False,"please enter a valid county"
    if msg_array[3] not in ["male","female"]:
        response = "please enter valid gender"
        return False,response
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
    if "+254" in number and len(number.replace("+254","0"))==10:
        return True,number.replace("+254","0")
    if len(number)==10 and (number[:2] == "07" or number[:2] == "01"):
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
    result_length,gender,results = fetch_match_count(message,gender)
    if result_length == 0:
        response = "No matches found for your request."
        return response
    else:
        response = f"""We have {result_length} {"ladies" if gender.strip()=="male"else"men"} who match your choice! We will send you details of 3 of them 
shortly.
To get more details about a {"man" if gender.strip()=="male"else"lady"}, SMS her number e.g., 0722010203 to 22141"""
        return response,results

def store_results(results):
    return results
def send_first_three(results):
    matches = []
    if len(results) > 1:
        first_three = results[:3]
        for match in first_three:
            match_info = f"{match[0]} aged {match[1]}, {match[2]}"
            matches.append(match_info)
        response = f"""{matches[0]}\n{matches[1]}\n{matches[2]} Send NEXT to 22141 to receive details of the remaining {len(results)-3} ladies"""
        # time.sleep(5)
        return response
def get_next_matches(number,gender):
    results,page = fetch_next_matches(number,gender)
    page_times_three = page*3
    results_length = len(results)-3
    difference = results_length - page_times_three
    if len(results)<6:
        next_three = results[3:]
        matches = []
        for match in next_three:
            match_info = f"{match[0]} aged {match[1]}, {match[2]}"
            matches.append(match_info)
        response = f"""{matches[0]}\n{matches[1]}\n{matches[2]}"""
        return response
    if len(results)>6 and page_times_three<=results_length:
        start_point = page*3
        end_point = start_point+3
        next_three = results[start_point:end_point]
        matches = []
        for match in next_three:
            match_info = f"{match[0]} aged {match[1]}, {match[2]}"
            matches.append(match_info)
        response = f"""{matches[0]}\n{matches[1]}\n{matches[2]}"""
        return response
    return "no more matches"

def message_router(message,number):
    number_is_valid,valid_number=number_checker(number)
    user_exists = check_if_user_exists(valid_number)
    if message == "penzi" and number_is_valid:
        if user_exists is None:
            response = send_first_message(valid_number)
            return response
    if "#" in message and message.split('#')[0]=="start" and number_is_valid and user_exists is None:
        is_valid,response = validate_registration(message)
        if is_valid:
            response = create_profile(valid_number,message)
            return response
        else:
            return response
    if '#' in message and message.split('#')[0]=="details":
        is_valid,response = validate_details(message)
        if is_valid:
            response = update_profile(valid_number,message)
            return response
        else:
            return response
    if len(user_exists)>1 and user_exists[6] is None:
        response = """You were registered for dating with your initial details.
To search for a MPENZI, SMS match#age#town to 22141 and meet the person of 
your dreams.
E.g., match#23-25#Nairobi"""
        insert_message(sender="22141",receiver=valid_number,message=response)
        return response
    if "myself" in message:
        response = update_description(valid_number,message)
        return response
    if "#" in message and "match" in message and len(user_exists)>1 and len(message.split('#')) == 3 and '-' in message.split('#')[1] and message.split('#')[2] in kenyan_counties:
        insert_message(sender=valid_number,receiver="22141",message=message)
        insert_match(user_number=valid_number,request=message,page_number=1)
        gender = fetch_gender(valid_number)
        resp1,results = get_number_of_matches(message,gender[0])
        resp2 = send_first_three(results)
        return  resp1 + resp2
    if "next" in message and len(user_exists) >1 and number_is_valid:
        insert_message(sender=valid_number,receiver="222141",message=message)
        next_occurrences = fetch_next_occurrences(valid_number)
        gender = fetch_gender(valid_number)
        matches = get_next_matches(valid_number,gender[0])
        insert_message(sender="22141",receiver=valid_number,message=matches)
        next_occurrences_counter = len(next_occurrences)+1
        insert_match(user_number=valid_number,request=matches,page_number= 2 if len(next_occurrences)==1 else next_occurrences_counter )
        return matches
    if "describe" in message and len(user_exists)>1 and:
        insert_message(sender=valid_number,receiver="22141",message=message)
        requested_number = message.replace("describe","").strip()
        name,description = fetch_description(requested_number)
        response = f"""{name} describes themselves as {description}"""
        return response
    if number_is_valid and len(user_exists)>1 and ("07" in message or "01" in message) and "describe" not in message:
        insert_message(sender=valid_number,receiver="22141",message=message)
        user_details = fetch_user_details(message)
        number,name,age,gender,county,city,level_of_education,profession,marital_status,ethnicity,religion = user_details
        response = f"""{name} aged {age}, {county} county, {city} town, {level_of_education}, {profession}, {marital_status}, {ethnicity}, {religion}"""
        requestor_details = fetch_user_details(valid_number)
        requestor_number,requestor_name,requestor_age,requestor_gender,requestor_county,requestor_city,requestor_level_of_education,requestor_profession,requestor_marital_status,requestor_ethnicity,requestor_religion = requestor_details
        inform_requested_message = f"""Hi {name} a {"man" if requestor_gender=="male" else "lady"}  is interested in you and requested your details.
        {"He" if requestor_gender=="male"else "She"} is aged {requestor_age} based in {requestor_county}.
        Do you want to know more about {"him"if requestor_gender=="male"else"her"}? Send YES to 22141"""
        insert_message(sender="22141",receiver=valid_number,message=response)
        insert_message(sender="22141",receiver=number,message=inform_requested_message)
        return response


