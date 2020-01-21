import os, sys, webbrowser, socket, threading
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from asyncio_socket import json_and_dict as jd

def open_browser():
    def check_django_status():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            return client.connect_ex(('127.0.0.1', 8000)) == 0
    data = jd.json2dict('./learn/jsons/my_data.json')
    handler = webbrowser.get()
    while not check_django_status():
        pass
    if data == {}:
        handler.open('http://127.0.0.1:8000/buddybook/first_login')
    else:
        handler.open("http://127.0.0.1:8000/buddybook/")


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'P2P.settings')
    application = get_wsgi_application()

    print("start_server: ", threading.enumerate())

    #start of code for develop time
    sys.argv.append('opened')
    try:
        os.remove("../learn/jsons/source.json")
    except FileNotFoundError:
        pass
    #end of code for develop time
    thread1 = threading.Thread(target=open_browser)
    if 'opened' not in sys.argv:
        thread1.start()
        sys.argv.append('opened')

    call_command('runserver', '127.0.0.1:8000')

