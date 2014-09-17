from google.appengine.api import channel


def __formServerToken__():
  import random
  rand = random.SystemRandom()
  
  import time
  currenttime = str(time.time())
  
  salt = ''.join(chr(rand.randint(65,90)) for x in range(10))

  return currenttime + salt


def create():
  server_token = __formServerToken__()
  client_token = channel.create_channel(server_token)
  return dict(client=client_token, server=server_token)


def send(token, message, freq='default'):
  message = {
    'frequency': freq,
    'message': message
  }
  from json import dumps
  message = dumps(message)
  channel.send_message(token, message)