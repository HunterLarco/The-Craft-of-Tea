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





class Guest:
  
  class post:
    
    @require('post','content')
    def comment(self, payload):
      try:
        identifier = int(payload['post'])
      except:
        return response.throw(201)
      
      from ..blog import posts
      
      post = posts.get(identifier)
      if post == None:
        return response.throw(200, data_struct=identifier)
      
      post.comment(payload['content'], handle=None if not 'handle' in payload else payload['handle'])





class Admin:
  
  class post:
    
    @require('identifier')
    def delete(self, payload):
      from ..blog import posts
      post = posts.get(payload['identifier'])
      if post == None:
        return response.throw(200, data_struct=identifier)
      post.delete()
    
    
    @require('content', 'title', 'author', 'identifier')
    def update(self, payload):
      from ..blog import posts
      post = posts.get(payload['identifier'])
      if post == None:
        return response.throw(200, data_struct=identifier)
      post.edit(payload['content'], author=payload['author'], title=payload['title'])
    
    
    @require('content', 'title', 'author')
    def create(self, payload):
      from ..blog import posts
      posts.create(payload['title'], payload['author'], payload['content'])


