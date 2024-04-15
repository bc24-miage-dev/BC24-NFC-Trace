import datetime

def get_date():
    date_now = datetime.datetime.now().strftime('%Y-%m-%d')
    print ("Getting date : " + date_now)
    return date_now