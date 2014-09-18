import webapp2
import os
from google.appengine.ext.webapp import template

from lib import api


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
        'identifier': post.id(),
        'content': post.content,
        'author': post.author,
        'title': post.title,
        'date': post.created,
        'next': post.next_post,
        'prev': post.prev_post,
        'comments': [{
          'handle':comment.handle,
          'date': comment.created,
          'content':comment.content
        } for comment in post.comments()]
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