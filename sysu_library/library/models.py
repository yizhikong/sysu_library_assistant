from django.db import models

# course in real world
class CourseNames(models.Model):
    cname = models.CharField(max_length = 100)
    description = models.CharField(max_length = 200)
    def __unicode__(self):
        return "Course name : " + cname

# book in real world
class BookNames(models.Model):
    bname = models.CharField(max_length = 100)
    description = models.CharField(max_length = 200)
    def __unicode__(self):
        return "Book name : " + bname

class Books(models.Model):
    bname = models.CharField(max_length = 100)
    isbn = models.CharField(max_length = 20)
    author = models.CharField(max_length = 100)
    publisher = models.CharField(max_length = 100)
    pic = models.CharField(max_length = 100)
    url = models.CharField(max_length = 60)
    def __unicode__(self):
        return "Book name : " + bname + "\nauthor : " + author + "\npublisher : " + publisher

class CourseRelation(models.Model):
    # one course has several correlated books
    course = models.ForeignKey(CourseNames)
    # not every book has relation with course, eg : search book directly by book name
    bid = models.IntegerField(default = 0)
    click = models.IntegerField(default = 0)

class BookRelation(models.Model):
    # one bookname has several correlated books in sysu library
    book = models.ForeignKey(BookNames)
    bid = models.IntegerField(default = 0)
    click = models.IntegerField(default = 0)