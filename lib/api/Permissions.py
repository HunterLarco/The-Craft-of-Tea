# common imports
import response
from .. import crawler


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











class Admin:
  
  class crawler:
    
    
    @require('key', 'channel')
    def ping(self, payload):
      crawl = crawler.model.get(payload['key'])
      if crawl == None:
        return response.throw(200, payload['key']);
      crawl.ping(payload['channel'])
    
    
    @require('domain')
    def create(self, payload):
      domain = payload['domain']
      channel_token = payload['channel']['token'] if 'channel' in payload and token in payload['channel'] else None
      
      kwarg_names = ['urlmatch', 'includedsubdomains', 'excludedsubdomains', 'includedmimetypes', 'excludedmimetypes', 'mapnakeddomains', 'stripurls']
      kargs = [payload[param] if param in payload else None for param in kwarg_names]
      
      crawl = crawler.model.create(domain, *kargs)
      connection = crawl.connect(channel_token)
      
      return response.reply({
        'connection': connection,
        'crawler': {
          'key': crawl.key.urlsafe()
        }
      })



