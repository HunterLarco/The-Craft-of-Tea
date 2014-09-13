from google.appengine.ext import deferred
from google.appengine.api import memcache
import channels


# token is the channel token to relay info to while the crawler works
def queue(domain, token=None, limitToRoot=False):
  domain = stripUrl(domain)
  memtoken = 'crawler-domain:(%s)-token:(%s)' % (domain, token)
  resetLinks(memtoken)
  resetTracker(memtoken)
  addLink(memtoken, domain)
  channels.send(token, {
    'type': 'log',
    'log': {
      'message': 'initiating crawler'
    }
  })
  deferred.defer(crawl, domain, domain, token, memtoken, limitToRoot)


def getPageContent(url):
  import urllib2
  return urllib2.urlopen(url)


def getLinksFromPage(pagecontent):
  from ..system.BeautifulSoup import BeautifulSoup
  import re
  soup = BeautifulSoup(pagecontent)
  links = soup.findAll('a')
  return links


def resetLinks(memtoken):
  memcache.set(memtoken, [])


def addLink(memtoken, link):
  links = memcache.get(memtoken)
  links.append(link)
  memcache.set(memtoken, links)


def getLinks(memtoken):
  return memcache.get(memtoken)


def stripUrl(url):
  from urlparse import urlparse
  uparse = urlparse(url)
  parse = ''.join(uparse[1:3])
  if parse[0:4] == 'www.':
    parse = parse[4:]
  parse = uparse[0]+'://'+parse
  if parse[-1:] == '/':
    parse = parse[:-1]
  return parse


def getUrlDomain(url):
  from urlparse import urlparse
  return '.'.join(urlparse(url).hostname.split('.')[-2:])


def resetTracker(memtoken):
  memcache.set(memtoken+'-(tracker)', 0)
def incrTracker(memtoken):
  memcache.incr(memtoken+'-(tracker)')
def decrTracker(memtoken):
  return memcache.decr(memtoken+'-(tracker)')


def crawl(domain, url, token, memtoken, limitToRoot=False):
  from urlparse import urljoin
  
  channels.send(token, {
    'type': 'log',
    'log': {
      'message': 'crawling over %s' % url
    }
  })
  
  content = getPageContent(url)
  newlinks = getLinksFromPage(content)
  
  urldomain = getUrlDomain(url)
  
  for link in newlinks:
    # interprets the link's location
    link = urljoin(url, link.get('href'))
    # strips parameters and #...
    link = stripUrl(link)
    
    channels.send(token, {
      'type': 'log',
      'log': {
        'message': 'processing %s' % link
      }
    })
    
    # limit links that we follow to the subdomain and base url we bagan traversing
    if limitToRoot and not link.startswith(domain):
      continue
    
    # skip links that lead to different domains (subdomains are ok)
    if getUrlDomain(link) != urldomain:
      continue
    
    if link in getLinks(memtoken):
      continue
    addLink(memtoken, link)
    
    channels.send(token, {
      'type': 'page',
      'page': {
        'location': link,
        'content': ''
      }
    })
    incrTracker(memtoken)
    deferred.defer(crawl, domain, link, token, memtoken, limitToRoot=limitToRoot)
  
  if(decrTracker(memtoken) == 0):
    channels.send(token, {
      'type': 'log',
      'log': {
        'message': 'crawler finished'
      }
    })
  