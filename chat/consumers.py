from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.conf import settings
from chat.models import Thread, Message
from account.models import Account
from django.shortcuts import redirect
import json
import datetime

class chatConsumer(WebsocketConsumer):
   def connect(self):
       me = self.scope['user']
       friend_username = self.scope['url_route']['kwargs']['username']
       friend = Account.objects.get(username = friend_username)
       self.thread_obj = Thread.objects.get_or_create_personal_thread(me, friend)
       self.room_name = f'presonal_thread_{self.thread_obj.id}'

       
       # allmessages=[]
       # messages = Message.objects.filter(thread = self.thread_obj)
       # for message in messages:
       #     allmessages.append((message.sender.username,message.text))
       # async_to_sync(self.channel_layer.group_send)(
       #  self.room_name,
       #     {
       #         'type': 'websocket.send',
       #         'message': 'allmessages',
       #     }
       # )

       # join room
       async_to_sync(self.channel_layer.group_add)(
           self.room_name,
           self.channel_name
       )
       # accept connection
       self.accept()


   def disconnect(self, close_code):
       async_to_sync(self.channel_layer.group_discard)(
           self.room_name,
           self.channel_name
       )
   # receive message from WebSocket
   def receive(self, text_data):
       text_data_json = json.loads(text_data)
       message = text_data_json['message']

       self.store_message(message)
       print(self.scope['user'].username)
       msg = json.dumps({
            'text': message,
            'username': self.scope['user'].username,
            'img': self.scope['user'].profile_img.url,
        })

       async_to_sync(self.channel_layer.group_send)(
        self.room_name,
           {
               'type': 'chat_message',
               'message': msg,
           }
       )

   def chat_message(self, event):
       self.send(text_data=json.dumps(event))

   def chat_messages(self, event):
       self.send(text_data=json.dumps(event))

   def store_message(self, text):
       Message.objects.create(
           thread = self.thread_obj,
           sender = self.scope['user'],
           text = text
       )
