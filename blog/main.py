import webapp2
import os
from google.appengine.ext.webapp import template


class PostHandler(webapp2.RequestHandler):
  def get(self, post_id=None):
    
    from lib.blog import posts
    
    if post_id:
      try:
        post_id = int(post_id)
      except:
        pass
    
    post = posts.get(post_id)
    
    if post == None:
      template_values = {}
      path = os.path.join(os.path.dirname(__file__), 'pages/404.html')
      self.response.out.write(template.render(path, template_values))
      return
  
    template_values = {
      'post': {
        'content': post.content,
        'date': post.created,
        'next': post.next_post,
        'prev': post.prev_post
      }
    }
    path = os.path.join(os.path.dirname(__file__), 'pages/post.html')
    self.response.out.write(template.render(path, template_values))


class APIHandler(webapp2.RequestHandler):
  def get(self, dictionary, method):
    api.delegate(self, dictionary, method, api.Permissions.Guest)
  def post(self, dictionary, method):
    api.delegate(self, dictionary, method, api.Permissions.Guest)


app = webapp2.WSGIApplication([('/api/([^/]+)/([^/]+)/?', APIHandler),
                               ('/([0-9]+)/?', PostHandler),
                               ('/.*', PostHandler)],
                               debug=True)