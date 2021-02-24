import requests
import json
import random

token = "1682805824:AAG2MVbi8xopExjM-Bre2kr0OyL8dclYbfk"
url = "https://api.telegram.org/bot" + token + "/"
MAX_QNS = 5

def generateList(qns):
    text = "<b>Send Halp Questions</b>"
    count = 1
    for qn in qns:
        text += "\n\n" + str(count) + ". " + qn['question'] + "\n"
        text += "[" + str(len(qn['answer'])) + " Ans]"
        count = count + 1
    return text

def main():
    rdm = random.randint(1, 10)
    questions = {}
    # questions is a dictionary with chat_id keys. Each key has an array (list) of
    # 5 qn dictionary, that contains a question string, user_id and an array (list)
    # of answer strings
    while True:
        result = requests.get(url + "getUpdates").json()
        if 'result' not in result:
            continue
        result = result['result']
        if len(result) == 0:
            continue # no results :(
        for message in result:
            if 'message' in message: # Message
                chat_id = message['message']['chat']['id']
                if chat_id not in questions:
                    questions[chat_id] = []
                chat_qns = questions[chat_id]

                if 'text' in message['message']: # Text
                    reply = message['message']['text']
                    args = reply.split(" ")
                    if args[0] == "/list":
                        if len(chat_qns) == 0:
                            text = "No questions to show! Ask one using /ask!"
                            message_out = {"chat_id": chat_id, "text": text}
                        else:
                            text = generateList(chat_qns)
                            buttons = [{"text": "1", "callback_data": "ans 1"}]
                            for i in range(2, len(chat_qns) + 1):
                                buttons.append({"text": str(i), "callback_data": "ans " + str(i)})
                            options = {"inline_keyboard": [buttons]}
                            message_out = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_markup": options}
                        requests.post(url + "sendMessage", json = message_out)

                    elif args[0] == "/remove":
                        if len(args) == 1:
                            text = "Please choose a question number!"
                            message_out = {"chat_id": chat_id, "text": text}
                            requests.post(url + "sendMessage", json = message_out)
                            continue
                        try: # test for non-integer input
                            qn_num = int(args[1])
                        except ValueError:
                            qn_num = 0
                        user_id = message['message']['from']['id']
                        if qn_num <= 0 or len(chat_qns) < qn_num:
                            text = "No such question to be removed! Please try again with another index!"
                        elif user_id != chat_qns[qn_num - 1]['user_id']:
                            text = "Sorry, you are not allowed to remove this question!"
                        else:
                            del chat_qns[qn_num - 1]
                            text = "Question " + args[1] + " has been removed!"
                        message_out = {"chat_id": chat_id, "text": text}
                        requests.post(url + "sendMessage", json = message_out)

                    elif args[0] == "/resolve":
                        if len(args) == 1:
                            text = "Please choose a question number!"
                            message_out = {"chat_id": chat_id, "text": text}
                            requests.post(url + "sendMessage", json = message_out)
                            continue
                        try: # test for non-integer input
                            qn_num = int(args[1])
                        except ValueError:
                            qn_num = 0
                        user_id = message['message']['from']['id']
                        if qn_num <= 0 or len(chat_qns) < qn_num:
                            text = "No such question to be resolved! Please try again with another index!"
                        elif user_id != chat_qns[qn_num - 1]['user_id']:
                            text = "Sorry, you are not allowed to resolve this question!"
                        else:
                            qn = chat_qns[qn_num - 1]
                            text = "<b>Question by " + qn['question'] + "</b>"
                            for ans in qn['answer']:
                                text += "\n\n" + ans
                            del chat_qns[qn_num - 1]
                        message_out = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
                        requests.post(url + "sendMessage", json = message_out)

                    elif args[0] == "/help":
                        ask = "Type /ask (question) here. Eg: /ask Where shall we go for lunch today?"
                        answer = "Type /answer (index) (answer) here. Eg: /answer 1 Hawker Centre"
                        list = "Type /list to display all the questions. Eg: /list"
                        remove = "Type /remove (index). Eg: /remove 2 - removes 2nd question in list"
                        resolve = "Type /resolve (index). Eg: /resolve 2 - removes 2nd question in list, prints out list afterwards"
                        sendhelp = "Type /sendhelp - cleans up the spam it creates afterwards"

                        message_out = {"chat_id": chat_id, "text": ask + "\n" + answer + "\n" + list + "\n" +remove
                                       + "\n" + resolve + "\n" + sendhelp}
                        requests.post(url + "sendMessage", json=message_out)

                    elif args[0] == "/sendhelp":
                        if len(args) == 1:
                            counts = 5
                        else:
                            try: # test for non-integer input
                                counts = int(args[1])
                                if counts > 10:
                                    counts = 10
                            except ValueError:
                                counts = 5
                        helpMessage = "Please help x " + str(counts) + "! :("
                        start = 1
                        end = counts + 1
                        message_out = {"chat_id": chat_id, "text": helpMessage}
                        deletelater = []
                        for i in range(start, end):
                            posted = requests.post(url + "sendMessage", json=message_out).content
                            parsed = json.loads(posted)
                            deletelater.append(parsed['result']['message_id'])
                            print(deletelater)
                        for i in range(start - 1, end - 1):
                            requests.post(url + "deleteMessage?" + "chat_id=" + str(chat_id) + "&message_id=" + str(
                                deletelater[i]))

                    elif args[0] == "/answer":
                        if len(args) == 1:
                            text = "Please write an answer!"
                            message_out = {"chat_id": chat_id, "text": text}
                            requests.post(url + "sendMessage", json = message_out)
                            continue
                        try: # test for non-integer input
                            qn_num = int(args[1])
                        except ValueError:
                            qn_num = 0
                        if qn_num <= 0 or qn_num > len(chat_qns): # out of range
                            text = "Invalid question number. Please try again!"
                            message_out = {"chat_id": chat_id, "text": text}
                            requests.post(url + "sendMessage", json = message_out)
                        elif len(args) == 2:
                            text = "Please write an answer!"
                            message_out = {"chat_id": chat_id, "text": text}
                            requests.post(url + "sendMessage", json = message_out)
                        else:
                            newAns = " ".join(args[2:])
                            qn = chat_qns[qn_num - 1]
                            user_name = message['message']['from']['first_name']
                            qn['answer'].append(user_name + ": " + newAns)
                            text = "<b>Question by " + qn['question'] + "</b>"
                            for ans in qn['answer']:
                                text += "\n\n" + ans
                            message_out = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
                            requests.post(url + "sendMessage", json = message_out)

                    elif args[0] == "/ping":
                        if rdm == 0:
                            rdm = random.randint(1, 10)
                            message_out = {"chat_id": chat_id, "text": "BANG BANG BANG"}
                        else:
                            rdm = rdm - 1
                            message_out = {"chat_id": chat_id, "text": "pong"}
                        requests.post(url + "sendMessage", json = message_out)

                    elif args[0] == "/ask":
                        if len(chat_qns) >= MAX_QNS:
                            text = "The maximum questions we can store is " + str(MAX_QNS) + ". Please /remove or /resolve the existing questions first."
                            message_out = {"chat_id": chat_id, "text": text}
                            requests.post(url + "sendMessage", json = message_out)
                        elif len(args) == 1:
                            text = "Please write a question!"
                            message_out = {"chat_id": chat_id, "text": text}
                            requests.post(url + "sendMessage", json = message_out)
                        else:
                            newQn = message['message']['from']['first_name'] + ": " + " ".join(args[1:])
                            user_id = message['message']['from']['id']
                            chat_qns.append({"question": newQn, "answer": [], "user_id": user_id})
                            text = generateList(chat_qns)
                            buttons = [{"text": "1", "callback_data": "ans 1"}]
                            for i in range(2, len(chat_qns) + 1):
                                buttons.append({"text": str(i), "callback_data": "ans " + str(i)})
                            options = {"inline_keyboard": [buttons]}
                            message_out = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_markup": options}
                            requests.post(url + "sendMessage", json = message_out)

            elif 'callback_query' in message:
                # print("Callback by " + callback_id)
                callback_id = message['callback_query']['id']
                data = message['callback_query']['data']
                args = data.split(" ")
                if args[0] == "ans": # show answers to a selected question
                    origin_msg = message['callback_query']['message']
                    chat_id = origin_msg['chat']['id']
                    chat_qns = questions[chat_id]
                    list_index = int(args[1]) - 1
                    if len(chat_qns) > list_index: # valid index
                        qn = chat_qns[int(args[1]) - 1]
                        text = "<b>Question by " + qn['question'] + "</b>"
                        for ans in qn['answer']:
                            text += "\n\n" + ans
                    else:
                        text = "Invalid question! Please try again."

                    pop_out = {"callback_query_id": callback_id}
                    message_out = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
                    requests.post(url + "answerCallbackQuery", json = pop_out)
                    requests.post(url + "sendMessage", json = message_out)

            offset = str(message['update_id'] + 1)
            result = requests.get(url + "getUpdates?offset=" + offset + "&timeout=1").json()

if __name__ == "__main__":
    main()
