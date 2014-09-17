from google.appengine.ext import ndb
from google.appengine.ext import deferred
from ..net import channels
import re


class Crawl(ndb.Model):
  
  channeltokens      = ndb.StringProperty(repeated=True)
  
  domain             = ndb.StringProperty()
  urlmatch           = ndb.StringProperty()
  includedsubdomains = ndb.StringProperty()
  excludedsubdomains = ndb.StringProperty()
  includedmimetypes  = ndb.StringProperty()
  excludedmimetypes  = ndb.StringProperty()
  mapnakeddomains    = ndb.BooleanProperty()
  stripurls          = ndb.BooleanProperty()
  
  queuedtime         = ndb.IntegerProperty()
  completedtime      = ndb.IntegerProperty()

  
  @ndb.transactional
  def queue(self):
    import time
    self.queuedtime = int(time.time())
    self.put()
  
  
  """
  ' PURPOSE
  '   Connects a user to the crawl's updates using a channel token
  """
  @ndb.transactional
  def connect(self, channel_token):
    if channel_token in self.channeltokens:
      return
    self.channeltokens.append(channel_token)
    self.put()
  
  
  """
  ' PURPOSE
  '   Sends a given message to all recipients connected to this crawl
  """
  def update(self, message):
    for channel in self.channeltokens:
      channels.send(channel, message, freq=self.key.urlsafe())




"""
' PURPOSE
'   Creates a new crawl entity given the parameters
' NOTES
'   1. Formats all necessary parameters to regex patterns
"""
def create(domain,
           urlmatch           = '.*',
           includedsubdomains = '.*',
           excludedsubdomains = '',
           includedmimetypes  = '.*',
           excludedmimetypes  = '',
           mapnakeddomains    = True,
           stripurls          = True):
  crawl = Crawl()
  crawl.domain             = domain
  crawl.urlmatch           = urlmatch
  crawl.includedsubdomains = includedsubdomains
  crawl.excludedsubdomains = excludedsubdomains
  crawl.includedmimetypes  = includedmimetypes
  crawl.excludedmimetypes  = excludedmimetypes
  crawl.mapnakeddomains    = mapnakeddomains
  crawl.stripurls          = stripurls
  crawl.channeltokens      = []
  crawl.queuedtime         = None
  crawl.completedtime      = None
  crawl.put()
  return crawl


def get(key):
  return ndb.Key(urlsafe=key).get()
