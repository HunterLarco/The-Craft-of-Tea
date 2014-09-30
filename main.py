import webapp2
import os
from google.appengine.ext.webapp import template

from lib import api


class MainHandler(webapp2.RequestHandler):
  def get(self):
    from lib.crawler import model
    import datetime
    template_values = {
      'crawls': [{
        'domain': crawl.domain,
        'urlmatch': crawl.urlmatch,
        'includedsubdomains': crawl.includedsubdomains,
        'excludedsubdomains': crawl.excludedsubdomains,
        'includedmimetypes': crawl.includedmimetypes,
        'excludedmimetypes': crawl.excludedmimetypes,
        'mapnakeddomains': crawl.mapnakeddomains,
        'stripurls': crawl.stripurls,
        'queueddate': datetime.datetime.fromtimestamp(crawl.queuedtime)
      } for crawl in model.queued()]
    }
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
