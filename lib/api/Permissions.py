# common imports
import response


### within this file, each root class defines what API functions are accessible by POST or GET. that way permission may be changed by simply instruction the API engine to delegate to a different permission map. For example, 'admin' indicates that api url '/constants/add' allows one to add a constant to the database, because a user doesn't have this privilage, their permission map lacks this ability. Note that GET requests must use the get dictionary exclusively








def require(*keys):
  def decorator(funct):
    def reciever(self, payload):
      for key in keys:
        if not key in payload:
          return response.throw(001)
      return funct(self, payload)
    return reciever
  return decorator








from .. import crawler




class Admin:
  
  """ -------------- BEGINNING OF CHANNEL DICT -------------- """
  
  class channel:
    
    @require('token')
    def ping(self, payload):
      from ..net import channels
      channels.send(payload['token'], {}, freq='ping')
    
    def connect(self, payload):
      from ..net import channels
      tokens = channels.create()
      return response.reply({
        'tokens': {
          'client': tokens['client']
        }
      })
  
  """ -------------- END OF CHANNEL DICT -------------- """
  
  
  
  
  
  
  """ -------------- BEGINNING OF CRAWLER DICT -------------- """
  
  class crawl:

    @require('domain', 'channel')
    def queue(self, payload):
      domain = payload['domain']
      channel_token = payload['channel']['token']
      options = payload['options'] if 'options' in payload else {}
      
      kwarg_names = [
        'urlmatch',
        'includedsubdomains',
        'excludedsubdomains',
        'includedmimetypes',
        'excludedmimetypes',
        'mapnakeddomains',
        'stripurls'
      ]
      kwargs = {}
      for param in kwarg_names:
        if param in options:
          kwargs[param] = options[param]
      
      crawl = crawler.model.create(domain, **kwargs)
      connection = crawl.connect(channel_token)
      crawl.queue()
      
      return response.reply({
        'crawl': {
          'key': crawl.key.urlsafe()
        }
      })

  """ -------------- END OF CRAWLER DICT -------------- """

