from datetime import datetime
import time
import logging
import re
import json
import urllib
import requests
import SearchCV


class TBot:
    # config
    LONG_POLL_TIME = 60
    printLogs=True
    token='313242842:AAFqsPhYL_TnYqKOL-3fbPY5YtZUZotbuTg'
    #num_of_lines = 0

    def __init__(self):
        print("Processing has began")
        #pass

    def wait(self, t = 60):
        time.sleep(t)
        if(self.printLogs):
            print("I woke up")
        return

    '''
    makes http request to telegram server
    parameters:
    	method - telegram api method (sendMessage, etc)
    	parameters - dict with key=parameter_name, value=parameter_value
	'''
    def request(self, method, parameters={}):
        TELEGRAM_API_ENDPOINT = 'https://api.telegram.org/bot{token}/{method}?{options}'
        HEADERS               = {'Content-type': 'application/json','Accept': 'text/plain'}
        ACCESS_TOKEN          = self.token

        data        = urllib.parse.urlencode(parameters)
        response    = requests.get(TELEGRAM_API_ENDPOINT.format(token=ACCESS_TOKEN,method=method,options=data),timeout=self.LONG_POLL_TIME,headers=HEADERS)

        return response

    def long_poll(self):
        NOW = int(datetime.now().strftime('%S'))
        LAST_REQUEST_ID = 0
        LAST_POLL_START = NOW

        while True:
            if(self.printLogs):
                print("getting response...")
            NOW = int(datetime.now().strftime('%S'))
            LAST_POLL_START = NOW
            try:
                response = self.request("getUpdates", {"offset": LAST_REQUEST_ID, 'timeout': self.LONG_POLL_TIME})
            except requests.exceptions.Timeout as e:
                print('Request timed out: {error}'.format(error = str(e)))
                continue

            if not response.status_code == requests.codes.ok:
                print('Update check call failed. Server responded with HTTP code: {code}'.format(code = response.status_code))
                self.wait()
                continue

            try:
                response_data = json.loads(response.text.strip())
            except ValueError as e:
                print('Parsing response Json failed with: {err}'.format(err = str(e)), end="\n\n")

                # Wait a little for the dust to settle and
                # retry the update call
                self.wait()
                continue

            if 'ok' not in response_data or not response_data['ok']:
                print('Response from Telegram API was not OK. We got: {resp}'.format(resp = str(response_data)), end="\n\n")
                continue

            # Check that some data was received from the API
            if not response_data['result']:
                print('This poll retreived no data')
                continue

            max_request_id  = max([x['update_id'] for x in response_data['result']])
            LAST_REQUEST_ID = max_request_id + 1 if ((max_request_id + 1) >= LAST_REQUEST_ID) else LAST_REQUEST_ID

            # main object - response object. Try to print it to look at its structure.
            #print("1")
            print(response_data)
            chat_id=response_data['result'][0]['message']['chat']['id']
            user_name = response_data['result'][0]['message']['chat']['first_name']
            print("Chat id: " + str(chat_id))
            if('text' in response_data['result'][0]['message']):
                text=response_data['result'][0]['message']['text']
                self.reply(text,chat_id,user_name)
            elif('sticker' in response_data['result'][0]['message']):
                lala=""
            elif ('photo' in response_data['result'][0]['message']):
                text="Фотки мне шлёшь, проказник? Ну, пошалим! \n Link:"
                file_id=response_data['result'][0]['message']['photo'][-1]['file_id']
                response_data=self.request('getFile',{'file_id':file_id})
                response_data = json.loads(response_data.text.strip())
                file_path = response_data['result']['file_path']
                print(file_path)
                fulltext =text + "https://api.telegram.org/file/bot" + self.token + "/" + file_path
                fileurl ="https://api.telegram.org/file/bot" + self.token + "/" + file_path
                print(fileurl)
                #self.reply(fulltext,chat_id,user_name)
                post_id=self.findSimilar(fileurl)
            #print("2")
            eval_request(response)

    def analizePhoto(self,photo):
        return "Это точно шаварма? Непонятно.."
    def planB(self,text,chat_id):
        text="Hey! I'm working!:)"
        self.request('sendMessage', {'chat_id': chat_id, 'text': text})

    '''This is the function, and it doesn't need improvements'''
    def reply(self, text, chat_id,user_name):
        text=str(text).lstrip().rstrip()
        if(text=='/howitworks'):
            print("Sending FAQs")
            self.request('sendMessage', {'chat_id': chat_id, 'text': "Как это работает? Магия, наверное..."})
            return
        if (text == '/start'):
            self.request('sendMessage', {'chat_id': chat_id,
                                         'text': "Привет, "+user_name+"! Я - главный анализатор всех шаверм.Пришли мне фотографию своей шавермы, и я скажу тебе какой она окажется!"})
            return
        if (text == '/howyoudoin'):
            self.request('sendMessage', {'chat_id': chat_id,
                                         'text': "Иногда я задумываюсь: какая она, совершенная шаверма?"})
            return
        if (text=='/sendpicture'):
            path=56
            self.request('sendMessage',{'chat_id':chat_id,'text':'Вот твоя фотка'})

        print("end all")
        print(text)
        self.request('sendMessage',{'chat_id':chat_id,'text':text})

    def extractpostid(self,string):
        result = ""
        counter = 0
        f = True
        for c in string:
            if (c == '.'):
                f = False
            if (counter == 3 and f):
                result += c
            if (c == '_'):
                counter = counter + 1
        return result

    def findSimilar(self,file_path):
        print(file_path)
        t = SearchCV.Finder()
        path = t.findpostid(file_path)
        post_id= self.extractpostid(path[1])
        print(post_id)
        return post_id
        #self.reply(text + "https://api.telegram.org/file/bot" + self.token + "/" + file_path, chat_id, user_name)

    ''' Just for example! '''
    '''
    def resend(self, response, chat_id):
        k = response.keys()
        if 'reply_to_message' in k:
            # it is a reply
            forward_m_id = response['reply_to_message']['message_id']
        else:
            if 'forward_from' in k:
                forward_m_id = response['message_id']
                if 'text' in k:
                    response['text'] = 'message forwarded...'
            else:
                forward_m_id = ''

        print(response)

        if 'text' in k:
            self.request('sendMessage',{'chat_id':chat_id, 'text':response['text'], 'reply_to_message_id': forward_m_id})
        if 'photo' in k:
            if isinstance(response['photo'], list):
                response['photo'] = response['photo'][0]
            a = self.request('sendPhoto',{'chat_id':chat_id, 'photo':response['photo']['file_id'], 'reply_to_message_id': forward_m_id})
        if 'audio' in k:
            self.request('sendAudio',{'chat_id':chat_id, 'audio':response['audio']['file_id'], 'reply_to_message_id': forward_m_id})
        if 'document' in k:
            self.request('sendDocument',{'chat_id':chat_id, 'document':response['document']['file_id'], 'reply_to_message_id':forward_m_id})
        if 'video' in k:
            self.request('sendVideo',{'chat_id':chat_id, 'video':response['video']['file_id'], 'reply_to_message_id': forward_m_id})
        if 'sticker' in k:
            self.request('sendSticker',{'chat_id':chat_id, 'sticker':response['sticker']['file_id'], 'reply_to_message_id': forward_m_id})
        if 'location' in k:
            self.request('sendLocation',{'chat_id':chat_id, 'latitude':response['location']['latitude'], 'longitude':response['location']['longitude'], 'reply_to_message_id': forward_m_id})
    '''

def eval_request(reponse):
    pass
    # do something


if __name__ == '__main__':
    T = TBot()

    T.long_poll()