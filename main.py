import webapp2
import os
from google.appengine.ext.webapp import template

from lib import api


class MainHandler(webapp2.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'crawler.html')
		self.response.out.write(template.render(path, template_values))


class APIHandler(webapp2.RequestHandler):
	def get(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Admin)
	def post(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Admin)


app = webapp2.WSGIApplication([
        ('/([^/]+)/([^/]+)/?', APIHandler),
        ('/.*', MainHandler)
      ], debug=True)
