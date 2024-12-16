import datetime

today = datetime.datetime.now()
weekday = today.weekday()

if weekday == 5 or weekday == 6:
    print(f"{today.strftime('%Y-%m-%d')} is Saturday or Sunday.")
else:
    print(f"{today.strftime('%Y-%m-%d')} is not Saturday or Sunday.")