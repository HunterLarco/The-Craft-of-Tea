import webapp2
from lib import api


class MainHandler(webapp2.RequestHandler):
	def get(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Admin)
	def post(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Admin)


app = webapp2.WSGIApplication([
        ('/admin/api/([^/]+)/([^/]+)/?', MainHandler)
      ], debug=True)
