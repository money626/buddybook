from django.shortcuts import render
import os
import shutil
import base64
import uuid
from django.http import JsonResponse, HttpResponse
from django.http.request import HttpRequest
from asyncio_socket import asyncio_server, requestHandle
from asyncio_socket import json_and_dict as jd
import json
import datetime

def timestamp():
    return datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S")

# Create your views here.
def index(request):
    #print(request.GET)
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    datas = [{'name': '秉寰神'}, {'name': '行之神'}]
    dataset = {'datas': datas}
    return render(request, "home.html", dataset)

def test_form(request):
    #print(request.GET)
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    return render(request, "test.html")

def send_request(request):
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    if request.FILES:
        #file = request.FILES["profile_picture"].read()
        #print(request.FILES)
        with open("./files/images/"+request.FILES["profile_picture"].name, "wb") as fp:
            for chunk in request.FILES["profile_picture"].chunks():
                fp.write(chunk)
    # if request.POST:
    #     print(request)
    #     for i in request.POST.keys():
    #         print(i, request.POST[i])
    # else:
    #     for i in request.GET.keys():
    #         print(i, request.GET[i])

def home(request):
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    article_dict =  asyncio_server.handler.article_dict
    my_data = asyncio_server.handler.my_data
    sorted_article_list = [k for k, v in sorted(article_dict.items(), key=lambda x:x[0])]
    articles = []
    for article_id in sorted_article_list:
        article = jd.json2dict(f'../learn/jsons/{article_id}.json')

        user_data = asyncio_server.handler.user_data_dict.get(article['owner_ID'])
        # if article_owner not in dict
        if user_data is None:
            # check if owner is self
            if article['owner_ID'] == my_data['ID']:
                article["user_name"] = my_data['user_name']
                article["img"] = my_data['profile_picture']
            else:
                continue
        else:
            article["user_name"] = user_data['user_name']
            article["img"] = my_data['profile_picture']
        print(article)
        articles.append(article)



    return render(request, "home.html", {"articles": articles, "my_id": my_data["ID"], "my_picture": my_data['profile_picture'], 'my_name': my_data['user_name']})

def my_articles(request):
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    article_list =  asyncio_server.handler.my_article_list
    my_data = asyncio_server.handler.my_data
    articles = []
    for article_id in article_list:
        article = jd.json2dict(f'../learn/jsons/{article_id}.json')

        user_data = asyncio_server.handler.user_data_dict.get(article['owner_ID'])
        # if article_owner not in dict
        if user_data is None:
            # check if owner is self
            if article['owner_ID'] == my_data['ID']:
                article["user_name"] = my_data['user_name']
                article["img"] = my_data['profile_picture']
            else:
                continue
        else:
            article["user_name"] = user_data['user_name']
            article["img"] = my_data['profile_picture']
        print(article)
        articles.append(article)



    return render(request, "home.html", {"articles": articles, "my_id": my_data["ID"], "my_picture": my_data['profile_picture'], 'my_name': my_data['user_name']})

def update_articles(request):
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    handler = asyncio_server.handler
    if len(handler.new_article_list):

        article_id = handler.new_article_list.pop(0)

        root_article_id = handler.new_comment_dict.get(article_id)
        handler.new_comment_dict.pop(article_id)
        if root_article_id is None:
            article = jd.json2dict(f"../learn/jsons/{article_id}.json")
        else:
            article = jd.json2dict(f"../learn/jsons/{root_article_id}.json")
        owner_data = handler.user_data_dict.get(article['owner_ID'])
        if owner_data is not None:
            article['user_name'] = owner_data['user_name']
            article['img'] = owner_data['profile_picture']
        else:
            return update_articles(request)
        return render(request, "article.html", {"article": article})
    else:
        return HttpResponse(" ", status=200)


def first_login(request):
    return render(request, "first_login.html")

def get_attr(request):
    if asyncio_server.handler.my_data == {}:
        print('error')
        return first_login(request)
    print(request.POST)
    print(request.FILES)
    for f in request.FILES.getlist('image'):
        print(f.name)
    #key = input('key = ')
    #print(request.POST[key])
    #print(my_request)
    #asyncio_server.handler.send_add_friend_reply(my_request, '127.0.0.1')
    return HttpResponse(str(uuid.uuid4()), status=200)

def send_add_friend_reply(request):
    if request.META['REQUEST_METHOD'] == 'GET':
        return HttpResponse(status=404)
    handler = asyncio_server.handler
    my_request = json.loads(request.POST['data'])
    my_data = handler.my_data
    request_id = my_request.pop('ID')
    my_request['body']['selfs_ID'] = my_data['ID']
    my_request['body']['user_name'] = my_data['user_name']
    handler.send_add_friend_reply(my_request, request_id)
    if my_request['body']['response']:
        handler.friend_list.append(request_id)
        handler.update_source()
    return render(request, "home.html", {'data': request.POST['data']})


def set_personal_data(request):
    if request.META['REQUEST_METHOD'] == 'POST':
        handler = asyncio_server.handler
        if handler.my_data != {}:
            try:
                os.remove("../learn/images/" + handler.my_data["profile_picture"])
                os.remove("../learn/images/" + handler.my_data["background_picture"])
            except FileNotFoundError:
                pass
            my_id = handler.my_data["ID"]
        else:
            my_id = str(uuid.uuid4())
        position = -1
        my_request ={'user_name': request.POST['user_name'], 'profile_context': request.POST['profile_context'], "ID": my_id, 'latest_edit_time':timestamp()}
        print(my_request)
        my_data = my_request.copy()
        for key in request.FILES.keys():
            while request.FILES[key].name[position] != '.':
                position -= 1

            picture = {"file_type": request.FILES[key].name[position + 1:]}
            file_name =  f"{str(uuid.uuid4())}.{picture['file_type']}"
            binary = []
            with open('../learn/images/' + file_name, 'wb') as fp:
                for chunk in request.FILES[key].chunks():
                    fp.write(chunk)
                    binary.append(chunk)
            picture["binary"] = str(base64.b64encode(b"".join(binary)), 'utf-8')
            my_data[key] = file_name
            my_request[key] = picture
        handler.lock.acquire()
        jd.dict2json('../learn/jsons/my_data.json', my_data)
        handler.lock.release()
        my_request = \
            {
                "header": "update_personal_data",
                "body": { "personal_data_list": [my_request] }
            }
        handler.send_update_personal_data(my_request)
        handler.my_data=my_data
        handler.user_data_dict[my_id] = \
            {
                "user_name": my_data['user_name'],
                "profile_picture": my_data['profile_picture']
            }
        return HttpResponse(status=200)
    return HttpResponse(status=404)

def add_friend(request):
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    return render(request, 'add_friend.html')

def send_add_friend(request):
    if request.META['REQUEST_METHOD'] == 'GET':
        return HttpResponse(status=404)
    if request.method == 'POST':
        target = request.POST['ip_address']

        asyncio_server.handler.lock.acquire()
        my_data_dict = jd.json2dict('../learn/jsons/my_data.json')
        asyncio_server.handler.lock.release()

        asyncio_server.handler.check_file_exists()
        with open(f'../learn/images/{my_data_dict["profile_picture"]}', 'rb') as fp:
            binary = fp.read()
            binary = str(base64.b64encode(binary), "utf-8")

        my_request = \
            {
                "header": 'add_friend_request',
                "body":
                    {
                        'selfs_ID': my_data_dict['ID'],
                        'user_name': my_data_dict['user_name'],
                        'profile_context': my_data_dict['profile_context'],
                        'profile_picture':
                            {
                                'file_type': my_data_dict['profile_picture'].split('.')[-1],
                                'binary': binary
                            }
                    }
            }
        print(requestHandle.verify_data(my_request['body'], my_request['header']))
        asyncio_server.handler.send_add_friend_request(my_request, target)
    else:
        return HttpResponse()
    return HttpResponse(status=200)
def reply(request):
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    request_list = []
    for ID in  asyncio_server.handler.friend_request_list:
        asyncio_server.handler.lock.acquire()
        my_request = jd.json2dict(f'../learn/jsons/{ID}.json')
        asyncio_server.handler.lock.release()
        if not os.path.exists(f'../learn/images/{my_request["profile_picture"]}'):
            my_request['profile_picture'] = f'{my_request["profile_picture"][:36]}.gif'
            shutil.copy('../learn/static/profile_picture_not_found.gif', f'../learn/images/{my_request["profile_picture"]}')
            asyncio_server.handler.lock.acquire()
            jd.dict2json(f'../learn/jsons/{ID}.json', my_request)
            asyncio_server.handler.lock.release()
        request_list.append(my_request)

    return render(request, 'friend_requests.html', {"request_list": request_list})

def add_article(request):
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    my_data = {'friend_list': asyncio_server.handler.friend_list}
    return render(request, 'add_article.html',{'data': my_data})

def my_data_page(request):
    if asyncio_server.handler.my_data == {}:
        return first_login(request)
    return render(request, "my_data.html", {'data': asyncio_server.handler.my_data})

def new_article_received(request):
    return render(request, "add_article.html")

def send_new_article(request):
    if not request.is_ajax():
        return HttpResponse(status=404)
    handler = asyncio_server.handler
    print(request.POST)
    image_content = []
    image_list = []
    for f in request.FILES.getlist('image'):
        file_type = f.name.split('.')[-1]
        file_name = f"{str(uuid.uuid4())}.{file_type}"
        image_list.append(file_name)
        binary = []
        with open(f'../learn/images/{file_name}', 'wb') as fp:
            for chunk in f.chunks():
                fp.write(chunk)
                binary.append(chunk)
        image_content.append({"file_type": file_type, "binary": str(base64.b64encode(b"".join(binary)), 'utf-8')})

    article_id = str(uuid.uuid4())
    try:
        my_article = \
            {
                "latest_edit_time": timestamp(),
                "article_ID": article_id,
                "owner_ID": asyncio_server.handler.my_data['ID'],
                "parent_ID": request.POST['parent_ID'],
                "root_article_ID": request.POST['root_article_ID'],
                "content": request.POST['content'],
                "image_content": image_content,
                "like_list": [],
                "position_tag": [i for i in request.POST.getlist('position_tag') if i != ""],
                "friend_tag": [i for i in request.POST.getlist('friend_tag') if i != ""],
                "comment_list": [],
                "deletion": False
            }
        my_request = \
            {
                "header": "post_article",
                "body": { "article_list": [my_article] }
            }
        handler.send_post_article(my_request)
        my_article["image_content"] = image_list
        handler.lock.acquire()
        jd.dict2json(f'../learn/jsons/{article_id}.json', my_article)
        handler.lock.release()
        if my_article['root_article_ID'] == "":
            root_article_id = article_id
            handler.my_article_list.append(article_id)
        else:
            root_article_id = my_article['root_article_ID']
            handler.lock.acquire()
            old_article = jd.json2dict(f'../learn/jsons/{root_article_id}.json')
            handler.lock.release()
            old_article['comment_list'].append(article_id)
            old_article['latest_edit_time'] = my_article['latest_edit_time']
            handler.lock.acquire()
            jd.dict2json(f'../learn/jsons/{root_article_id}.json', old_article)
            handler.lock.release()


        handler.article_dict[root_article_id] = my_article['latest_edit_time']
        handler.update_source()
        handler.send_post_article(my_request)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    if my_article['root_article_ID'] != '':
        return HttpResponse(str(uuid.uuid4()), status=200)
    my_article["user_name"] = handler.my_data['user_name']
    my_article["img"] = handler.my_data['profile_picture']
    return render(request, "article.html", {"article": my_article})

def send_like_up(request, article_id):
    article_id = str(article_id)
    self_id = asyncio_server.handler.my_data["ID"]
    old_data = jd.json2dict(f"../learn/jsons/{article_id}.json")
    old_data['like_list'].append(self_id)
    jd.dict2json(f"../learn/jsons/{article_id}.json", old_data)
    my_request = \
        {
            "header": "like_up",
            "body":
                {
                    "self_ID": self_id,
                    "article_ID": article_id,
                    "latest_edit_time": timestamp()
                }
        }
    asyncio_server.handler.send_like_up(my_request)
    return HttpResponse(status=200)

def like_list(request, article_id):
    article_id = str(article_id)
    article = jd.json2dict(f"../learn/jsons/{article_id}.json")
    user_list = []
    for user_id in article['like_list']:
        user_data = asyncio_server.handler.user_data_dict.get(user_id)
        if user_data is not None:
            user_list.append(user_data['user_name'])
    print(user_list)
    return render(request, "like_list.html", {"user_list": user_list})
