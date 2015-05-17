from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from library.models import *
from course_reptile.reptile import CourseReptile
# from library.bookCrawler import getBooksListByName

'''
------------------------------------
search books by couse name
return the result as xml
service for android application
------------------------------------
'''
def searchByCourse(requset):
    course = requset.GET.get("course", "")
    if course == "":
        return HttpResponse("Request error") 
    try:
        # check whether this couse is in database
        c = CourseNames.objects.get(cname = course)
        # return the historic result
        xml =  getExistCourseRecord(c)
        return HttpResponse(xml, mimetype="application/xml")
    except CourseNames.DoesNotExist:
        # this course has not been searched before
        # search it, and store the result in database
        cr = CourseReptile()
        booksNames = cr.course_search(course)
        # if not correlated book for this course
        if not len(booksNames):
            return HttpResponse("No relative book for this course!")
        c = CourseNames.objects.create(cname = course, description = "")
        c.save()
        xml = ""
        for bookName in booksNames:
            # to be implement. this operation should return a list of dictionary
            books = getBooksListByName(bookName = bookName, num = 3)
            # some database operation
            for book in books:
                # book is a dictionary
                bookid = storeBookItem(book)
                # construct the return xml
                xml += getBookItemXml(bookid)
                # create the relation for this new course and the the relative book
                r = CourseRelation.objects.create(course = c, bid = bookid, click = 0)
                r.save()
        if xml == ""：
            return HttpResponse("No relative book for this course!")
        xml = packXml(xml, c.id, "course")
        return HttpResponse(xml, mimetype="application/xml")

# service for function searchByCourse
def getExistCourseRecord(course_object):
    relations = course_object.courserelation_set.all()
    bookids = [r.bid for r in relations]
    xml = ""
    for bookid in bookids:
        xml += getBookItemXml(bookid)
    return packXml(xml, course_object.id, "course")

'''
--------------------------------------------------------------------------
the following three function search for both course search and book search
--------------------------------------------------------------------------
'''

# add the parent node to the xml
def packXml(xml, sid, search_type):
    head = '''<?xml version="1.0" encoding="UTF-8"?>\n''' +\
           '''<bookList id = "%d" type = "%s">\n'''
    tail = '''</bookList>'''
    resXml = (head % (sid, search_type)) + xml + tail
    return resXml

# create an xml for a book
def getBookItemXml(bookid):
    try:
        b = Books.objects.get(id = bookid)
    except Books.DoesNotExist:
        return ""
    item_xml = '<item>\n' +\
                   '<name>%s</name>\n' +\
                   '<pic>%s</pic>\n' +\
                   '<author>%s</author>\n' +\
                   '<publisher>%s</publisher>\n' +\
                   '<isbn>%s</isbn>\n' +\
               '</item>\n'
    item_xml = item_xml % (b.name, b.pic, b.author, b.publisher, b.isbn)
    return item_xml

# store a book item into database
# item is a dictionary, has keys : name, pic, author, publisher, isbn, detail
def storeBookItem(item):
    try:
        b = Books.objects.get(bname = item.name, author = item.author, num = item.num)
        return b.id
    except:
    b = Books.objects.create(bname = item.name, publisher = item.publisher,
                            author = item.author, pic = item.pic,
                            isbn = item.isbn, url = item.url)
    b.save()
    return b.id


'''
----------------------------------------------------------
search books directly by book name
return the result as xml
service for android application
the logic is different from the function "searchByCourse"!
----------------------------------------------------------
'''
def searchByBook(requset):
    course = requset.GET.get("book", "")
    if course == "":
        return HttpResponse("Request error") 
    try:
        # check whether this book is in database
        b = BookNames.objects.get(bname = course)
        # return the historic result
        xml =  getExistBookRecord(b)
        return HttpResponse(xml, mimetype="application/xml")
    except BookNames.DoesNotExist:
        # this book name has not been searched before
        # search it, and store the result in database
        # books is a list of dictionary
        books = wait_for_xiongtao_api()
        # if not correlated book for this course
        if not len(booksNames):
            return HttpResponse("No relative book in sysu library!")
        b = BookNames.objects.create(bname = course, description = "")
        b.save()
        xml = ""
        # some database operation
        for book in books:
            # book is a dictionary
            bookid = storeBookItem(book)
            # construct the return xml
            xml += getBookItemXml(bookid)
            # create the relation for this new course and the the relative book
            r = BookRelation.objects.create(book = b, bid = bookid, click = 0)
            r.save()
        if xml == ""：
            return HttpResponse("No relative records for this book!")
        xml = packXml(xml, b.id, "book")
        return HttpResponse(xml, mimetype="application/xml")

# maybe this function should merge with getExistCourseRecord
# but I think it is not a good idea
def getExistBookRecord(book_object):
    relations = book_object.bookrelation_set.all()
    bookids = [r.bid for r in relations]
    xml = ""
    for bookid in bookids:
        xml += getBookItemXml(bookid)
    return packXml(xml, book_object.id, "course")

'''
-----------------------------------------------------------------
return the detail message for a book by xml
the augument is isbn, which is the primary key for a book records
-----------------------------------------------------------------
'''
def getBookDetail(requset):
    isbn = requset.GET.get("isbn", "")
    if isbn == "":
        return HttpResponse("Request error")
    try:
        b = Books.objects.get(isbn = isbn)
    except BooksDoesExist:
        return HttpResponse("ISBN error")
    xml = '<book>\n' +\
              '<name>%s</name>\n' +\
              '<pic>%s</pic>\n' +\
              '<author>%s</author>\n' +\
              '<publisher>%s</publisher>\n' +\
              '<isbn>%s</isbn>\n' +\
              '<position>%s</position>\n' +\
              '<available>%s</available>\n' +\
              '<digest>%s</digest>\n' +\
          '</book>\n'
    return HttpResponse(xml, mimetype="application/xml")

def clickIncrement(requset):
    # sid means seach id
    sid = requset.GET.get("sid", "")
    isbn = requset.GET.get("isbn", "")
    search_type = requset.GET.get("search_type", "")
    if search_type == "course":
        try:
            c = CourseNames.objects.get(id = sid)
            b = Books.objects.get(isbn = isbn)
            r = CourseRelation.objects.get(course = c, bid = b.id)
            r.click += 1
            r.save()
        except:
            return HttpResponse("Relation error")
    if search_type == "book":
        try:
            bn = BookNames.objects.get(id = sid)
            b = Books.objects.get(isbn = isbn)
            r = BookRelation.objects.get(book = c, bid = b.id)
            r.click += 1
            r.save()
        except:
            return HttpResponse("Relation error")
    return HttpResponse("Request error")