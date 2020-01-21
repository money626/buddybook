from django.urls import path
from . import views
from django.conf.urls.static import static
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


urlpatterns = [
    path('', views.index),
    path('test_form/', views.test_form),
    path('home/', views.home, name='home'),
    path('first_login/', views.first_login, name='first_login'),
    path('update_articles/', views.update_articles, name='update_articles'),
    path('get_attr/', views.get_attr, name='get_attr'),
    path('set_data/', views.set_personal_data, name='set_data'),
    path('add_friend/', views.add_friend, name='add_friend'),
    path('send_add_friend/', views.send_add_friend, name='send_add_friend'),
    path('add_article/', views.add_article, name='add_article'),
    path('friend_requests/', views.reply, name='friend_requests'),
    path('send_add_friend_reply/', views.send_add_friend_reply, name='send_add_friend_reply'),
    path('my_data/', views.my_data_page, name='my_data'),
    path('new_article_received/', views.new_article_received, name="new_article_received"),
    path('send_new_article/', views.send_new_article, name='send_new_article'),
    path('send_like/<uuid:article_id>/', views.send_like_up, name="send_like"),
    path('like_list/<uuid:article_id>/', views.like_list, name="like_list"),
    path('my_articles/', views.my_articles, name="my_articles")
]
urlpatterns += static('media/', document_root=os.path.join(BASE_DIR, 'images'))
urlpatterns += static('static/', document_root=os.path.join(BASE_DIR, 'static'))
import asyncio, threading

loop = asyncio.new_event_loop()
def run_loop(new_loop):
    new_loop.run_forever()
from asyncio_socket.asyncio_server import run_main
socket_thread = threading.Thread(target=run_main, name='socket-thread')
socket_thread.start()
# asyncio_thread = threading.Thread(target=run_loop, args=(loop, ), name='asyncio_thread')
# asyncio_thread.start()