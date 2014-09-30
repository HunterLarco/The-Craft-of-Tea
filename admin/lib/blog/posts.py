"""
' Common Imports
"""
from google.appengine.ext import ndb


"""
' PURPOSE
'   The post model class, used to save entities to the
'   ndb datestore
"""
class Post(ndb.Model):
  
  # date created
  created = ndb.DateTimeProperty(auto_now_add=True)
  # post content (HTML)
  content = ndb.TextProperty()
  title = ndb.StringProperty(indexed=True)
  author = ndb.StringProperty(indexed=True)
  # next and previous posts
  prev_post = ndb.IntegerProperty()
  next_post = ndb.IntegerProperty()
  
  def edit(self, content, author=None, title=None):
    self.content = content
    if author:
      self.author = author
    if title:
      self.title = title
    self.put()
    
  
  def delete(self):
    prevpost = self.prev()
    nextpost = self.next()
    if prevpost != None:
      prevpost.next_post = nextpost.id() if nextpost else None
      prevpost.put()
    if nextpost != None:
      nextpost.prev_post = prevpost.id() if prevpost else None
      nextpost.put()
    for comment in self.comments():
      comment.delete()
    self.key.delete()
  
  def comments(self):
    import comments
    return comments.fetch(self)
  
  def comment(self, content, handle=None):
    import comments
    comments.create(self, content, handle)
  
  def prev(self):
    if not self.prev_post:
      return None
    return self.__class__.get_by_id(self.prev_post)
  
  def next(self):
    if not self.next_post:
      return None
    return self.__class__.get_by_id(self.next_post)
  
  def id(self):
    return self.key.id()
  
  def toDict(self):
    return {
      'identifier': self.id(),
      'content': self.content,
      'author': self.author,
      'title': self.title,
      'date': self.created,
      'next': self.next_post,
      'prev': self.prev_post,
      'comments': [{
        'handle':comment.handle,
        'date': comment.created,
        'content':comment.content
      } for comment in self.comments()]
    }


"""
' PURPOSE
'   Creates a new post with the given content, it also simultaneously
'   updates the next_post field of the post prior to this new one
' PARAMETERS
'   <str content>
' RETURNS
'   <Post extends ndb.Model>
"""
def create(title, author, content):
  prev_post = getNewest()
  
  post = Post()
  post.content = content
  post.author = author
  post.title = title
  post.prev_post = prev_post.id() if prev_post else None
  post.put()
  
  if prev_post != None:
    __updateNextPost__(prev_post, post)
  
  return post


"""
' PURPOSE
'   A private method that updates the next_post field
'   of a post
' PARAMETERS
'   <Post extends ndb.Model post>
'   <Post extends ndb.Model next_post>
' RETURNS
'   None
"""
@ndb.transactional
def __updateNextPost__(post, next_post):
  post.next_post = next_post.id()
  post.put()


"""
' PURPOSE
'   Returns the most recently written post
' PARAMETERS
'   Nothing
' RETURNS
'   <Post extends ndb.Model> or None
"""
def getNewest():
  return Post.query().order(-Post.created).get()


"""
' PURPOSE
'   Returns all the current posts ordered by their creation date
' PARAMETERS
'   Nothing
' RETURNS
'   A list of <Post extends ndb.Model>
"""
def all():
  return Post.query().order(-Post.created).fetch()


"""
' PURPOSE
'   Returns the post corresponding with the given identifier (post id)
'   if no id is provided, it returns the most recently written post.
' PARAMETERS
'   <int **kwarg identifier>
' RETURNS
'   <Post extends ndb.Model> or None
"""
def get(identifier=None):
  if identifier == None:
    return getNewest()
  try:
    post = Post.get_by_id(int(identifier))
  except:
    return None
  return post