import datetime

def get_date():
    date_now = datetime.datetime.now().strftime('%Y-%m-%d')
    print("Date actuel : "+date_now)
    return date_now

print(get_date())