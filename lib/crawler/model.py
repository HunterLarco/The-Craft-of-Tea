from google.appengine.ext import ndb
from google.appengine.ext import deferred
from ..net import channels
import re


class Crawl(ndb.Model):
  
  channeltokens      = ndb.StringProperty(repeated=True)
  
  domain             = ndb.StringProperty(indexed=True)
  urlmatch           = ndb.StringProperty()
  includedsubdomains = ndb.StringProperty()
  excludedsubdomains = ndb.StringProperty()
  includedmimetypes  = ndb.StringProperty()
  excludedmimetypes  = ndb.StringProperty()
  mapnakeddomains    = ndb.BooleanProperty()
  stripurls          = ndb.BooleanProperty()
  
  queuedtime         = ndb.IntegerProperty()
  completedtime      = ndb.IntegerProperty()
  
  
  """ CONSTANTS """
  CRAWL_STARTED  = 'cw0'
  CRAWL_QUEUED   = 'cw1'
  CRAWL_COMPLETE = 'cw2'
  PING_RESPONSE  = 'cw3'
  
  
  # def queue(self):
    # from google.appengine.ext import deferred
  
  
  def ping(self, channel_token):
    channels.send(channel_token, {
      'type': self.PING_RESPONSE
    }, freq=self.key.urlsafe())
  
  
  """
  ' PURPOSE
  '   Connects a user to the crawl's updates. They can provide
  '   a pre-existing channel token or None. If there isn't one
  '   one will be assigned.
  """
  def connect(self, channel_token=None):
    channel_client_token = None
    
    if channel_token == None:
      channel = channels.create()
      channel_token = channel['token']
      channel_client_token = channel['client']
    
    self.__addChannelToken__(channel_token)
    
    return dict(
      client    = channel_client_token,
      token     = channel_token,
      constants = dict(
        CRAWL_STARTED  = self.CRAWL_STARTED,
        CRAWL_QUEUED   = self.CRAWL_QUEUED,
        CRAWL_COMPLETE = self.CRAWL_COMPLETE,
        PING_RESPONSE  = self.PING_RESPONSE
      )
    )


  """
  ' PURPOSE
  '   Adds a channel token to this entity and then saves it.
  """
  @ndb.transactional
  def __addChannelToken__(self, token):
    if token in self.channeltokens:
      return
    self.channeltokens.append(token)
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
  crawl = Crawl(
    domain             = domain,
    urlmatch           = urlmatch,
    includedsubdomains = includedsubdomains,
    excludedsubdomains = excludedsubdomains,
    includedmimetypes  = includedmimetypes,
    excludedmimetypes  = excludedmimetypes,
    mapnakeddomains    = mapnakeddomains,
    stripurls          = stripurls,
    channeltokens      = [],
    queuedtime         = None,
    completedtime      = None
  )
  crawl.put()
  return crawl


def get(key):
  return ndb.Key(urlsafe=key).get()
