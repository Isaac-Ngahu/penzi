import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  database="penzi",
  port=3306,
  password="12976"
)


def check_if_user_exists(number):
  sql = "SELECT * FROM user where Number = %s "
  value = (number,)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql, value)
    result = mycursor.fetchall()
    if len(result) == 1:
      return True
    return False
  finally:
    mycursor.close()

def insert_initial_message(number, response):
  sql = "INSERT INTO message (sender,receiver,message) VALUES (%s,%s,%s)"
  values = ("22141", number, response)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql, values)
    mydb.commit()
  finally:
    mycursor.close()

def create_user(number,name,age,gender,county,city):
  sql ="INSERT INTO user (Number,Name,Age,Gender,County,City) VALUES (%s,%s,%s,%s,%s,%s)"
  values = (number,name,age,gender,county,city)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql, values)
    mydb.commit()
  finally:
    mycursor.close()

def insert_message(sender,receiver,message):
  sql = "INSERT INTO message (sender,receiver,message) VALUES(%s,%s,%s)"
  values = (sender,receiver,message)
  mycursor =mydb.cursor()
  try:
    mycursor.execute(sql, values)
    mydb.commit()
  finally:
    mycursor.close()

def add_user_details(number,level_of_education,profession,marital_status,ethnicity,religion):
  sql = """
    UPDATE user
    SET LevelOfEducation = %s,
        Profession = %s,
        MaritalStatus = %s,
        Ethnicity = %s,
        Religion = %s
    WHERE Number = %s
    """
  values=(level_of_education,profession,marital_status,ethnicity,religion,number)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql, values)
    mydb.commit()
  finally:
    mycursor.close()

def record_description(number,message):
  new_message = message.replace("myself","")
  sql = "UPDATE user SET Description=%s WHERE Number=%s"
  values =(new_message.strip(),number)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql, values)
    mydb.commit()
  finally:
    mycursor.close()


def fetch_gender(number):
  sql = "SELECT Gender FROM user WHERE Number=%s"
  values = (number,)

  mycursor = mydb.cursor()

  try:
    mycursor.execute(sql, values)
    gender = mycursor.fetchone()
    return gender
  finally:
    mycursor.close()


def fetch_match_count(message,gender):
  activator,age_range,county = message.split("#")
  start_age,end_age = age_range.split("-")
  sql_q = "SELECT Name,Age,Number FROM user WHERE COUNTY=%s AND Age BETWEEN %s AND %s AND Gender=%s ORDER BY TImeCreated DESC"
  vals = (county, start_age, end_age,"female" if gender=="male" else "male")
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql_q, vals)
    results = mycursor.fetchall()
    return  gender,results
  finally:
    mycursor.close()

def insert_match(user_number,request,page_number):
  sql = "INSERT INTO matches (UserNo,MatchRequest,PageNo) VALUES (%s,%s,%s)"
  values = (user_number,request,page_number)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql, values)
    mydb.commit()
  finally:
    mycursor.close()

def get_matches(message,gender):
  activator, age_range, county = message.split("#")
  start_age, end_age = age_range.split("-")
  sql1 = "SELECT Name,Age,Number FROM user WHERE Gender=%s AND Age BETWEEN %s AND %s ORDER BY TImeCreated DESC"
  values1 = ("female"if gender == "male" else "male", start_age, end_age)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql1, values1)
    results = mycursor.fetchall()
    return results
  finally:
    mycursor.close()

def fetch_next_matches(number,gender):
  mycursor = mydb.cursor()
  try:
    sql = """
          SELECT MatchRequest, PageNo
          FROM matches
          WHERE UserNo = %s AND MatchRequest LIKE 'match#%'
          ORDER BY TimeReceived DESC
          """
    value = (number,)
    mycursor.execute(sql, value)

    result = mycursor.fetchall()
    if len(result[0])==2:
      match_request, page = result[0]
      activator, age_range, county = match_request.split("#")
      start_age, end_age = age_range.split("-")
      mycursor.close()
      mycursor = mydb.cursor()
      sql1 = "SELECT Name, Age, Number FROM user WHERE Gender = %s AND Age BETWEEN %s AND %s"
      values1 = ("female" if gender == "male" else "male", start_age, end_age)
      mycursor.execute(sql1, values1)

      results = mycursor.fetchall()

      return results, page
  finally:
    # Ensure the cursor is closed if it hasn't been already
    if mycursor:
      mycursor.close()

def fetch_next_occurrences(number):
  sql = "SELECT message FROM message WHERE sender=%s and message LIKE 'next%'"
  value = (number,)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql,value)
    result = mycursor.fetchall()
    return result
  finally:
    mycursor.close()

# def get_database_connection():
#   try:
#     mydb.ping(reconnect=True, attempts=3, delay=2)  # Ping to check and reconnect if necessary
#     return mydb
#   except mysql.connector.Error as err:
#     print(f"Error connecting to MySQL: {err}")
#     return None
def fetch_user_details(number):
  sql = "SELECT Number,Name,Age,Gender,County,City,LevelOfEducation,Profession,MaritalStatus,Ethnicity,Religion FROM user WHERE Number=%s"
  values = (number,)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql,values)
    details = mycursor.fetchall()
    return details
  finally:
    mycursor.close()

def fetch_description(number):
  sql = "SELECT Name,Description from user WHERE Number=%s"
  value = (number,)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql,value)
    description = mycursor.fetchall()
    if len(description)==1:
      return description
    return []
  finally:
    mycursor.close()

def get_requestor_number(number):
  sql = "SELECT sender FROM message WHERE message=%s ORDER BY TimeSent DESC"
  value = (number,)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql, value)
    sender = mycursor.fetchall()
    return sender[0][0]
  finally:
    mycursor.close()


def check_for_requestor(number):
  sql = "SELECT sender, message FROM message WHERE message = %s"
  value = (number,)
  mycursor = mydb.cursor()
  try:
    mycursor.execute(sql, value)
    sender = mycursor.fetchall()
    if len(sender) > 0:
      sql = "SELECT Name, Age, County FROM user WHERE Number = %s"
      value = (sender[0][0],)
      mycursor.execute(sql, value)
      details = mycursor.fetchall()
      if len(details) > 0 and len(details[0]) == 3:
        return True, details[0]
    return False, []
  finally:
    mycursor.close()


print(type(get_requestor_number("0788378499")))
# print(fetch_user_details(str(0742292991)))
