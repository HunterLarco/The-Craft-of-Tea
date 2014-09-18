import webapp2


class APIHandler(webapp2.RequestHandler):
	def get(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Admin)
	def post(self, dictionary, method):
		api.delegate(self, dictionary, method, api.Permissions.Admin)


app = webapp2.WSGIApplication([('/[(^/]+)/([^/]+)/?', APIHandler)],
                            debug=True)
