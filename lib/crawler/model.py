from google.appengine.ext import ndb
from google.appengine.ext import deferred
from ..net import channels


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


  def crawl(self):
    self.update({
      'type': 'log',
      'message': 'Crawl Queued'
    })
    deferred.defer(self.__crawl__, [], [self.domain])
  
  
  def __crawl__(self, used_urls, queued_urls):
    from urlparser import Url
    import re
    
    
    new_urls = []
    
    
    for url in queued_urls:
      url = Url(url)
      
      if self.stripurls:
        url.strip()
      if self.mapnakeddomains:
        url.mapNaked()
      
      self.update({
        'type': 'log',
        'message': 'Inspecting %s' % url.url()
      })
      
      used_urls.append(url.url())
      
      
      try:
        if url.url().index(used_urls[0]) != 0:
          self.update({
            'type': 'log',
            'message': 'Skipping %s\n\tBase-URL Mismatch' % url.url()
          })
      except:
        self.update({
          'type': 'log',
          'message': 'Skipping %s\n\tBase-URL Mismatch' % url.url()
        })
      
      
      if self.includedsubdomains and not url.matchesSubdomain(self.includedsubdomains):
        self.update({
          'type': 'log',
          'message': 'Skipping %s\n\tSubdomain Mismatch' % url.url()
        })
        continue
      if self.excludedsubdomains and url.matchesSubdomain(self.excludedsubdomains):
        self.update({
          'type': 'log',
          'message': 'Skipping %s\n\tExcluded Subdomain' % url.url()
        })
        continue
      
      content = url.get()
      mimetype = content.info().type
      
      if mimetype != None:
        if self.includedmimetypes and re.match(re.compile(self.includedmimetypes), mimetype) == None:
          self.update({
            'type': 'log',
            'message': 'Skipping %s\n\tMimetype Mismatch %s' % (url.url(), mimetype)
          })
          continue
        if self.excludedmimetypes and re.match(re.compile(self.excludedmimetypes), mimetype) != None:
          self.update({
            'type': 'log',
            'message': 'Skipping %s\n\tExcluded Mimetype %s' % (url.url(), mimetype)
          })
          continue
      
      
      from ..util.BeautifulSoup import BeautifulSoup
      soup = BeautifulSoup(content)
      links = soup.findAll('a')
      
      for link in links:
        from urlparse import urljoin
        link = urljoin(url.url(), link.get('href'))
        if not link in used_urls:
          new_urls.append(link)
      
      if not self.urlmatch or url.matchesUrl(self.urlmatch):
        self.update({
          'type': 'page',
          'text': soup.get_text(),
          'url': url.url()
        })
      
    if len(new_urls) == 0:
      return
    
    deferred.defer(self.__crawl__, used_urls, new_urls)

  
  """
  ' PURPOSE
  '   Queues the crawl and locks further queues
  ' PARAMETERS
  '   None
  ' RETURNS
  '   A boolean
  '     True if queued
  '     False if failed
  """
  def queue(self):
    if self.queuedtime != None:
      return False
    self.__updateQueueTime__()
    self.crawl()
    return True
  
  
  """
  ' PURPOSE
  '   A private method to set the queue time for this entity
  """
  @ndb.transactional
  def __updateQueueTime__(self):
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
  crawl.urlmatch           = urlmatch           if urlmatch           != '' else None
  crawl.includedsubdomains = includedsubdomains if includedsubdomains != '' else None
  crawl.excludedsubdomains = excludedsubdomains if excludedsubdomains != '' else None
  crawl.includedmimetypes  = includedmimetypes  if includedmimetypes  != '' else None
  crawl.excludedmimetypes  = excludedmimetypes  if excludedmimetypes  != '' else None
  crawl.mapnakeddomains    = mapnakeddomains
  crawl.stripurls          = stripurls
  crawl.channeltokens      = []
  crawl.queuedtime         = None
  crawl.completedtime      = None
  crawl.put()
  return crawl


def get(key):
  return ndb.Key(urlsafe=key).get()


def queued():
  return Crawl.query(Crawl.queuedtime != None).order(-Crawl.queuedtime).fetch()


def all():
  return Crawl.query().fetch()