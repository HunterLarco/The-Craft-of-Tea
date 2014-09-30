"""
' Common Imports
"""
from google.appengine.ext import ndb


"""
' PURPOSE
'   The comment model class, used to save entities to the
'   ndb datestore
"""
class Comment(ndb.Model):
  
  # date created
  created = ndb.DateTimeProperty(auto_now_add=True)
  # post content
  content = ndb.TextProperty()
  handle = ndb.StringProperty()

  def id(self):
    return self.key.id()
  
  def reply(self, *args, **kwargs):
    return create(self, *args, **kwargs)
  
  def replies(self, *args, **kwargs):
    return fetch(self, *args, **kwargs)


"""
' PURPOSE
'   Returns all the comments associated with the provided post
' PARAMETERS
'   <Post extends ndb.Model>
' RETURNS
'   <ndb.Query contains <Comment extents ndb.Model>>
' NOTES
'   The comments are ordered with the most recent first
"""
def fetch(post):
  return Comment.query(ancestor=post.key).order(-Comment.created).fetch()


"""
' PURPOSE
'   Creates a new comment on a post
' PARAMETERS
'   <post Post extends ndb.Model>
'   <str content>
'   <str **kwarg handle=None> (like an author)
' RETURNS
'   <Comment extends ndb.Model>
"""
def create(post, content, handle=None):
  comment = Comment(parent=post.key)
  
  comment.content = content
  comment.handle = handle
  comment.put()

  return comment