import webapp2
import os
from google.appengine.ext.webapp import template


class MainHandler(webapp2.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'pages/main.html')
		self.response.out.write(template.render(path, template_values))


class APIHandler(webapp2.RequestHandler):
	def get(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Guest)
	def post(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Guest)


app = webapp2.WSGIApplication([('/.*', MainHandler),
                               ('/api/[(^/]+)/([^/]+)/?', APIHandler)],
                            debug=True)
