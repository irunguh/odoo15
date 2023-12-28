import os
import redis
import json
import requests
import connection
def send_a_file(chatID, phone_number, image_link, file_name, caption_text,token):
    # try to send a file for each request
    file_data = {
        "chatID": chatID,
        "phone": phone_number,
        # "body": "https://upload.wikimedia.org/wikipedia/ru/3/33/NatureCover2001.jpg",
        "body": image_link,
        "filename": file_name,
        "caption": caption_text,
        "token": token
    }
    print("Debug:::: MESSAGE SUBSCRIBER::::: send data to chat-api :::::: ")
    print(file_data)
    answer = send_requests('sendFile', file_data)
    print("debug:::: send_requests response in send_a_file {0}".format(answer))

    return answer


# borrowed from whatsapp chat api function
"""
function to send message back to ChatAPI
"""


def send_message(company_id, phone_no, text):

    data = {"chatID": "450380",
            "phone": phone_no,
            "body": text}
    # print("Send Message {} ".format(data))
    print("Debug::::: Send Message ::::")
    print(data)
    answer = send_requests('sendMessage', data)
    print("debug:::: send_requests in send_message response {0}".format(answer))
    # #try to send a file for each request
    # file_data = {
    #     "chatID": chatID,
    #      "phone": phone_number[0],
    #      "body":  "https://upload.wikimedia.org/wikipedia/ru/3/33/NatureCover2001.jpg",
    #      "filename": "NatureCover2001.jpg",
    #      "caption": "Fonscom Real Estate Test"
    # }
    # send_file = send_requests('sendFile',file_data)

    return answer


"""
function to send requests
"""


def send_requests(method, data):
    ##
    # self.dict_messages = json['messages']
    #APIUrl = "https://api.chat-api.com/instance{0}/".format(data.get('chatID'))
    APIUrl = "https://api.1msg.io/{0}/".format(data.get('chatID'))
    token = data.get('token')
    ####
    url = f"{APIUrl}{method}?token={token}"
    # url = "{}{}?token={}".format({self.APIUrl,method,self.token})
    print("URL >>>>>>>> ")
    print(url)
    headers = {'Content-type': 'application/json'}
    # print('Data to send {} '.format(data))
    answer = requests.post(url, data=json.dumps(data), headers=headers)
    print("Debug::: Chat API Stats ")
    print(answer)
    to_json = False
    try:
        to_json = answer.json()
        return to_json
    except Exception as e:
        print("Debug::: Chat API responded with an Error: ")
        print(e)
        return to_json
def subscriber():
    redis_conn = redis.Redis(charset="utf-8", decode_responses=True)
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("broadcast_to_users")

    for message in pubsub.listen():
        if message.get("type") == "message":
            to_json = json.loads(message.get("data"))
            print(to_json)
            # we send data to chat api
            # to_json = json.loads(body)
            send_file = send_a_file(to_json.get('chatID'), to_json.get('phone'), to_json.get('body'),
                                         'banner.jpeg', to_json.get('caption'),to_json.get('token'))
            print("debug: After sending information to phone number")
            #print(send_file)
            #send_data_state = 'failed'
            send_data_state = ''
            try:
				    
                    if send_file.get('send') == None:
                        send_data_state = 'failed'
                    else:
                        send_data_state = send_file.get('send')

                    data_to_create = {
                        'name': to_json.get('chatID'),
                        'phone': to_json.get('phone'),
                        'message': to_json.get('caption'),
                        'send_state': send_data_state,
                        'status_message': send_file.get('message')

                    }
                    print("Send data")
                    print(data_to_create)
                    result = connection.object.execute_kw(
                        connection.db, connection.uid, connection.password,
                        'whatsapp.redis.queue', 'create',
                        [data_to_create])

                    print("Debug::::: Report creation with {0}".format(result))
            except Exception as e:
                print(e)
                #return result
if __name__ == "__main__":
    print("Debug::: Start subscriber::::::::: ")
    subscriber() ;
