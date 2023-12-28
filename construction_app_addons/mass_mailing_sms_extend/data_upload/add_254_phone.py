import pandas as pd
import math

df = pd.read_csv("gp1b.csv")

# format phone number
def format_customer_phone_no(number):
    print(number)
    phone = str(number)
    formated_phone = None
    # length
    if len(phone) > 13 and len(phone) < 10:
        return False
    # starts with 254
    if phone.startswith('254'):
        new_phone = '+' + phone
        formated_phone = new_phone
        return formated_phone
    # starts with zero
    elif phone.startswith('0'):
        new_phone = phone.lstrip('0')
        new_phone = '+254' + new_phone
        formated_phone = new_phone
        return formated_phone
    # starts with +
    elif phone.startswith('+254'):
        formated_phone = phone
        return formated_phone
    elif phone.startswith('7'):
        formated_phone = phone
        return formated_phone
    # whatever
    else:
        return False

#Filtering the dataframe with the function
df = df[df["mobile"].apply(format_customer_phone_no)]

#df.drop(df.index[(df["score1] == '')], axis=0,inplace=True)

df.to_csv('cleaned/gp1b_clean.csv')
