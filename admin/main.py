from google.appengine.ext.webapp import template
import webapp2
import os


from lib import api
class APIHandler(webapp2.RequestHandler):
	def get(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Admin)
	def post(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Admin)


class MainHandler(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'urls.html')
    self.response.out.write(template.render(path, template_values))


class NewPostHandler(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'tools/newpost.html')
    self.response.out.write(template.render(path, template_values))


class PostManager(webapp2.RequestHandler):
  def get(self):
    from lib.blog import posts
    template_values = {
      'posts' : [post.toDict() for post in posts.all()]
    }
    path = os.path.join(os.path.dirname(__file__), 'tools/postmanager.html')
    self.response.out.write(template.render(path, template_values))


class EditingManager(webapp2.RequestHandler):
  def get(self, post_id):
    from lib.blog import posts
    template_values = {
      'post': posts.get(post_id).toDict()
    }
    path = os.path.join(os.path.dirname(__file__), 'tools/editor.html')
    self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([('/([^/]+)/([^/]+)/?', APIHandler),
                               ('/newpost/?', NewPostHandler),
                               ('/manager/?', PostManager),
                               ('/manager/edit/([0-9]+)/?', EditingManager),
                               ('/.*', MainHandler)
                              ], debug=True)
