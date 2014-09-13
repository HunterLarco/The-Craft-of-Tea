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











class Admin:
  
  class crawler:
    
    @require('domain', 'token')
    def queue(self, payload):
      from ..net import crawler
      crawler.queue(payload['domain'], token=payload['token'])
    
    def connect(self, payload):
      from ..net import channels
      channel = channels.create()
      return response.reply({
        'channel': {
          'token': channel['token'],
          'key': channel['key']
        }
      })



