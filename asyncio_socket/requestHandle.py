from asyncio_socket import json_and_dict as jd
import uuid
import base64
import os
import json
import threading
import asyncio
from asyncio_socket import send_request_handle
from asyncio_socket import asyncio_server
import shutil

sync_data = []
request_types = ["add_friend_request", "add_friend_reply", "update_personal_data", "post_article", "like_up", "sync1_request", "sync1_response", "sync2_request"]
useful_keys = \
{
    str: ["selfs_ID", "user_name", "profile_context", "ID", "latest_edit_time", "article_ID", "content", "owner_ID", "file_type", "binary","parent_ID", "root_article_ID","current_ID_type", "self_ID"],
    dict: ["profile_picture","background_picture"],
    list: ["article_list", "data_list","like_list", "image_content", "position_tag", "friend_tag","personal_data_list"],
    bool: ["response", "deletion"],
    "add_friend_request": ["selfs_ID", "user_name", "profile_picture", "profile_context"],
    "add_friend_reply": ["selfs_ID", "response"],
    "update_personal_data":["personal_data_list"],
    "personal_data_list":["ID", "user_name", "profile_picture","background_picture","latest_edit_time","profile_context"],
    "post_article": ["article_list"],
    "like_up": ["article_ID","self_ID","latest_edit_time"],
    "sync1_request": ["data_list"],
    "sync1_response":["data_list"],
    "sync2_request":["data_list"],
    "article_list":["article_ID", "content", "owner_ID" ,"like_list","position_tag","friend_tag", "image_content", "latest_edit_time","parent_ID", "root_article_ID","deletion"],
    "profile_picture":["file_type", "binary"],
    "image_content":["file_type", "binary"],
    "background_picture":["file_type", "binary"],
    "data_listsync1_request":["ID", "latest_edit_time", "current_ID_type"],
    "data_listsync1_response":["ID", "latest_edit_time", "current_ID_type"],
    "data_listsync2_request":["ID", "current_ID_type"]
}


def verify_data(data, request_type):
    if type(data) is not dict:
        return False
    useless_keys = [key for key in data.keys() if key not in useful_keys[request_type]]


    print("Before remove", data.keys())
    for key in useless_keys:
        data.pop(key)
    print("After remove", data.keys())

    for key in useful_keys[request_type]:
        if key not in data.keys():
            print(f'Missing {key}')
            return False
    for key in data.keys():
        print(f'Checking {key}')

        key_type = type(data[key])
        print(f'Key type: {key_type}')
        if key not in useful_keys[key_type]:
            print('wrong type!')
            return False
        if key_type == list:
            if key == "article_list":
                for child_object in data[key]:
                    if not verify_data(child_object, key):
                        return False
            elif key == "data_list":
                for child_object in data[key]:
                    if not verify_data(child_object, key + request_type):
                        return False
            elif key == "personal_data_list":
                for child_object in data[key]:
                    if not verify_data(child_object, key):
                        return False

            else:
                for child_object in data[key]:
                    if key == 'image_content':
                        if not verify_data(child_object, key):
                            return False

        elif key_type == dict:
            if not verify_data(data[key], key):
                return False

    return True

class RequestHandler:
    def __init__(self, loop):
        self.lock = threading.Lock()
        self.loop = loop
        lists = jd.json2dict('../learn/jsons/source.json')


        if lists == {}:
            self.friend_list = []
            self.friend_request_list = []
            self.article_dict = {}
            self.waiting_response_list = []
            self.ip_address_dict = {}
            self.my_article_list = []
            self.user_data_dict = {}
            self.comment_dict = {}
            self.update_source()
        else:
            self.friend_list = lists['friend_list']
            self.friend_request_list = lists['friend_request_list']
            self.article_dict = lists['article_dict']
            self.waiting_response_list = lists['waiting_response_list']
            self.ip_address_dict = lists['ip_address_dict']
            self.my_article_list = lists['my_article_list']
            self.user_data_dict = lists['user_data_dict']
            self.comment_dict = lists['comment_dict']
        self.my_data = jd.json2dict('../learn/jsons/my_data.json')
        self.new_article_list = []
        self.new_comment_dict = {}
        if self.my_data != {}:
            self.check_file_exists()
            if self.user_data_dict == {}:
                self.user_data_dict[self.my_data['ID']] = \
                    {
                        "user_name": self.my_data['user_name'],
                        "profile_picture": self.my_data['profile_picture']
                    }


    def check_file_exists(self):
        if not os.path.exists(f'../learn/images/{self.my_data["background_picture"]}'):
            file_name = f'{self.my_data["background_picture"][:36]}.png'
            print('Background not found')
            print('Copying not found image...')
            shutil.copy('../learn/static/background_not_found.png', f'../learn/images/{file_name}')
            self.my_data["background_picture"] = file_name
            jd.dict2json('../learn/jsons/my_data.json', self.my_data)
        if not os.path.exists(f'../learn/images/{self.my_data["profile_picture"]}'):
            file_name = f'{self.my_data["profile_picture"][:36]}.gif'
            print('Profile picture not found')
            print('Copying not found image...')
            shutil.copy('../learn/static/profile_picture_not_found.gif', f'../learn/images/{file_name}')
            self.my_data["profile_picture"] = file_name
            jd.dict2json('../learn/jsons/my_data.json', self.my_data)

    def request_handle(self, request, peername):

        try:
            data = request["body"]
            request_type = request["header"]
            print(f'Request: {request_type}')
        except KeyError:
            self.bad_request()
            return
        if request_type not in request_types:
            self.bad_request()
            return
        if not verify_data(data, request_type):
            print("verify failed")
            self.bad_request()
            return
        else:
            print("verify passed")
        # switch cases
        {
            "add_friend_request": lambda: self.add_friend_request(data, peername),
            "add_friend_reply": lambda: self.add_friend_reply(data, peername),
            "update_personal_data": lambda: self.update_personal_data(data),
            "post_article": lambda: self.post_article(data),
            "like_up": lambda: self.like_up(data),
            "sync1_request": lambda: self.sync1_request(data),
            "sync1_response": lambda: self.sync1_response(data),
            "sync2_request": lambda: self.sync2_request(data)
        }.get(request["header"], lambda: self.bad_request())()

    def add_friend_request(self, data, peername):
        print('add_friend')
        if data['selfs_ID'] in self.friend_list:
            return
        picture = data["profile_picture"]
        file_type = picture["file_type"]
        binary = picture["binary"]
        file_name = self.save_picture(file_type, binary, 'profile_picture')
        json_path = f"../learn/jsons/{data['selfs_ID']}.json"
        print(json_path)
        self.lock.acquire()
        js = jd.json2dict(json_path)
        self.lock.release()
        print(js)
        if js != {}:
            try:
                os.remove(f"../learn/images/{js['profile_picture']}")
            except FileNotFoundError:
                pass
        data["profile_picture"] = file_name
        self.lock.acquire()
        jd.dict2json(json_path, data)
        self.lock.release()
        if data['selfs_ID'] not in self.friend_request_list:
            self.ip_address_dict[data['selfs_ID']] = peername[0]
            self.friend_request_list.append(data['selfs_ID'])
            self.update_source()

    def add_friend_reply(self, data, peername):
        print(self.waiting_response_list)
        if peername[0] not in self.waiting_response_list:
            print(peername[0])
            return
        self.waiting_response_list.remove(peername[0])
        if data["response"]:
            self.friend_list.append(data['selfs_ID'])
            self.ip_address_dict[data['selfs_ID']] = peername[0]
            self.send_personal_data(peername[0])
        self.update_source()

    def update_personal_data(self, data):
        #loop through list
        for personal_data in data['personal_data_list']:
            #read old_data
            self.lock.acquire()
            old_data = jd.json2dict(f'../learn/jsons/{personal_data["ID"]}.json')
            self.lock.release()
            if old_data != {}:
                #skip if old_data is newer than current one
                if old_data.get("latest_edit_time") is not None:
                    if old_data['latest_edit_time'] > personal_data['latest_edit_time']:
                        continue
                    try:
                        #remove old pictures
                        os.remove("../learn/images/" + old_data["profile_picture"])
                        os.remove("../learn/images/" + old_data["background_picture"])
                    except FileNotFoundError:
                        pass
                else:
                    try:
                        #remove old pictures
                        os.remove("../learn/images/" + old_data["profile_picture"])
                    except FileNotFoundError:
                        pass
            #save pictures and put file_name to json
            picture = personal_data["profile_picture"]
            file_name = self.save_picture(picture['file_type'], picture['binary'], 'profile_picture')
            personal_data["profile_picture"] = file_name
            picture = personal_data["background_picture"]
            file_name = self.save_picture(picture['file_type'], picture['binary'], 'background_picture')
            personal_data["background_picture"] = file_name
            json_path = f'../learn/jsons/{personal_data["ID"]}.json'
            #update json file
            self.lock.acquire()
            jd.dict2json(json_path, personal_data)
            self.lock.release()
            self.user_data_dict[personal_data["ID"]] = {"user_name": personal_data["user_name"], "profile_picture": personal_data["profile_picture"]}
            self.update_source()

    def post_article(self, data):
        articles = []
        for article in data["article_list"]:
            # if no parent -> root article
            if article["parent_ID"] == "":
                if article['owner_ID'] in self.friend_list:
                    articles.append(article)
            else:
                if article["root_article_ID"] in self.article_dict.keys():
                    self.lock.acquire()
                    jd.dict2json(f"../learn/jsons/{article['article_ID']}.json", article)
                    self.lock.release()
                    old_data = jd.json2dict(f"../learn/jsons/{article['root_article_ID']}.json")
                    if article['article_ID'] not in  old_data['comment_list']:
                        old_data['comment_list'].append(article['article_ID'])
                    old_data['latest_edit_time'] = article['latest_edit_time']
                    jd.dict2json(f'../learn/jsons/{article["root_article_ID"]}.json', old_data)
                    self.article_dict[article["root_article_ID"]] = article['latest_edit_time']
                    self.new_comment_dict[article["article_ID"]] = article["root_article_ID"]
                    self.new_article_list.append(article["article_ID"])
                    self.update_source()
                    return


        for article in articles:
            # if article is on local -> compare edit time
            if self.article_dict.get(article['article_ID']) is not None:
                if self.article_dict[article['article_ID']] > article['latest_edit_time']:
                    continue
            image_list = []
            for image in article["image_content"]:
                image_list.append(self.save_picture(image['file_type'], image['binary']))
            article['image_content'] = image_list
            article['comment_list'] = []
            jd.dict2json(f'../learn/jsons/{article["article_ID"]}.json', article)
            # set local article edit time to received article edit time
            self.article_dict[article['article_ID']] = article['latest_edit_time']
            self.new_article_list.append(article['article_ID'])
        self.update_source()

    def like_up(self, data):
        if data['article_ID'] in self.article_dict.keys():
            json_path = f"../learn/jsons/{data['article_ID']}.json"
            self.lock.acquire()
            article = jd.json2dict(json_path)
            self.lock.release()
            if article == {}:
                return
            article["like_list"].append(data["self_ID"])
            article["latest_edit_time"] = data["latest_edit_time"]
            self.lock.acquire()
        elif data['article_ID'] in self.comment_dict.keys():
            json_path = f"../learn/jsons/{self.comment_dict.get(data['article_ID'])}.json"
            self.lock.acquire()
            article = jd.json2dict(json_path)
            self.lock.release()
            if article == {}:
                return
            article["like_list"].append(data["self_ID"])
            article["latest_edit_time"] = data["latest_edit_time"]
            self.lock.acquire()
        else:
            return
        jd.dict2json(json_path, article)
        self.lock.release()

    def sync1_request(self, data):
        pass

    def sync1_response(self, data):
        pass

    def sync2_request(self, data):
        pass

    def update_source(self):
        js = \
            {
                "friend_list": self.friend_list,
                "friend_request_list": self.friend_request_list,
                "article_dict": self.article_dict,
                "waiting_response_list": self.waiting_response_list,
                "ip_address_dict": self.ip_address_dict,
                "my_article_list": self.my_article_list,
                "comment_dict": self.comment_dict,
                "user_data_dict": self.user_data_dict
            }
        self.lock.acquire()
        jd.dict2json('../learn/jsons/source.json', js)
        self.lock.release()

    @staticmethod
    def bad_request():
        print("Bad Request")

    @staticmethod
    def save_picture(file_type, binary, data_type='profile_picture'):
        file_name = str(uuid.uuid4())
        try:
            with open(f"../learn/images/{file_name}.{file_type}", "wb") as fp:
                fp.write(base64.b64decode(binary))
            file_name += f'.{file_type}'
        except base64.binascii.Error:
            print("image broken")
            if data_type == 'background_picture':
                file_name += '.png'
                shutil.copy('../learn/static/background_not_found.png', f'../learn/images/{file_name}')
            if data_type == 'profile_picture':
                file_name += '.gif'
                shutil.copy('../learn/static/profile_picture_not_found.gif', f'../learn/images/{file_name}')

        return file_name



    def send_add_friend_request(self, request, target):

        asyncio.run_coroutine_threadsafe(send_request_handle.client_main(json.dumps(request), target), self.loop)
        if target in self.waiting_response_list:
            return
        self.waiting_response_list.append(target)
        self.update_source()

    def send_add_friend_reply(self, request, target_ID):
        self.friend_request_list.remove(target_ID)
        target = self.ip_address_dict.get(target_ID)
        self.check_file_exists()
        asyncio.run_coroutine_threadsafe(send_request_handle.client_main(json.dumps(request), target), self.loop)
        if request['body']['response']:
            self.send_personal_data(target)
        self.update_source()

    def send_personal_data(self, target):
        with open(f'../learn/images/{self.my_data["background_picture"]}', 'rb') as fp:
            background_picture = str(base64.b64encode(fp.read()), "utf-8")
        with open(f'../learn/images/{self.my_data["profile_picture"]}', 'rb') as fp:
            profile_picture = str(base64.b64encode(fp.read()), "utf-8")
        my_data = \
            {
                "header": "update_personal_data",
                "body":
                    {
                        "personal_data_list":
                            [
                                {
                                    "ID": self.my_data["ID"],
                                    "user_name": self.my_data["user_name"],
                                    "background_picture":
                                        {
                                            "binary": background_picture, 'file_type':
                                            self.my_data['background_picture'].split('.')[-1]
                                        },
                                    "profile_context": self.my_data["profile_context"],
                                    "profile_picture":
                                        {
                                            "binary": profile_picture,
                                            'file_type': self.my_data['profile_picture'].split('.')[1]
                                        },
                                    "latest_edit_time": self.my_data["latest_edit_time"]
                                }
                            ]
                    }
            }
        asyncio.run_coroutine_threadsafe(send_request_handle.client_main(json.dumps(my_data), target), self.loop)

    def send_update_personal_data(self, request):
        for target_ID in self.friend_list:
            target = self.ip_address_dict[target_ID]
            data = asyncio.run_coroutine_threadsafe(send_request_handle.client_main(json.dumps(request),target), self.loop)
            print(data.result())

    def send_post_article(self, request):
        for target_ID in self.friend_list:
            target = self.ip_address_dict[target_ID]
            asyncio.run_coroutine_threadsafe(send_request_handle.client_main(json.dumps(request),target), self.loop)

    def send_like_up(self, request):
        for target_ID in self.friend_list:
            target = self.ip_address_dict[target_ID]
            asyncio.run_coroutine_threadsafe(send_request_handle.client_main(json.dumps(request), target), self.loop)
