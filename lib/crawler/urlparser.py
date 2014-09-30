class Url(object):
  
  def __init__(self, url):
    from urlparse import urlparse
    components = urlparse(url)
    self.components = dict(
      scheme     = components.scheme,
      host       = '.'.join(components.netloc.split('.')[-2:]),
      subdomains = components.netloc.split('.')[:-2],
      path       = components.path,
      hash       = '#%s' % components.fragment,
      params     = '?%s' % components.query
    )


  def matchesUrl(self, regex_str):
    import re
    return re.match(re.compile(regex_str), self.components['path']) != None
  
  
  def matchesSubdomain(self, regex_str):
    import re
    return re.match(re.compile(regex_str), '.'.join(self.components['subdomains'])) != None
  

  def mapNaked(self):
    if len(self.components['subdomains']) == 0:
      self.components['subdomains'].append('www')


  def strip(self):
    self.components['params'] = ''
    self.components['hash'] = ''

  
  def url(self):
    return '%s://%s%s%s%s%s' % (
      self.components['scheme'],
      '.'.join(self.components['subdomains']) + ('.' if len(self.components['subdomains']) > 0 else ''),
      self.components['host'],
      self.components['path'],
      self.components['params'],
      self.components['hash']
    )
  
  
  def get(self):
    import urllib2
    return urllib2.urlopen(self.url())