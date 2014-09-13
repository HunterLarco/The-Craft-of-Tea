from google.appengine.api import channel


def __formid__():
  import random
  rand = random.SystemRandom()
  
  import datetime
  time = datetime.datetime.now().strftime("%s")
  
  salt = ''.join(chr(rand.randint(65,90)) for x in range(10))

  return time+salt


def create():
  ID = __formid__()
  token = channel.create_channel(ID)
  return dict(key=token, token=ID)


def send(token, message):
  if not isinstance(message, str):
    from json import dumps
    message = dumps(message)
  channel.send_message(token, message)