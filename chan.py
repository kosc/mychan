#!/usr/bin/env python
from pymongo import MongoClient
import tornado.web
from tornado.web import RequestHandler
import tornado.template

client = MongoClient()
db = client.chandb


class MainHandler(RequestHandler):

    def get(self):
        boards = db.boards.find({}, {'name': 1, 'desc': 1})
        self.render("templates/index.html", boards=boards)


class BoardHandler(RequestHandler):

    def get(self, brd):
        board = db.boards.find_one({'name': brd})
        dbthreads = db.threads.find({'board': brd})
        threads = []
        for dbthread in dbthreads:
            posts = db.posts.find({'thread': dbthread['number']})
            thread = [dbthread]
            for post in posts:
                thread.append(post)
            threads.append(thread)
        self.render("templates/board.html", 
                    board=board, 
                    threads=threads)

    def post(self, board):
        title = self.get_argument("title", None)
        message = self.get_argument("message", None)
        number = max_number()
        file_name = ''
        if 'image' in self.request.files:
            image_body = self.request.files['image'][0]['body']
            file_name = board + '_' + str(number) + '.jpg'
            img = open('static/images/' + file_name, 'wb')
            img.write(image_body)
        db.threads.insert({
            'board': board, 
            'number': int(number), 
            'title': title, 
            'text': message,
            'image': file_name})
        self.redirect("/" + board + "/")


class ThreadHandler(RequestHandler):

    def get(self, board, number):
        thread = list(db.threads.find({'number': int(number)}))
        posts = list(db.posts.find({'thread': number}))
        thread += posts
        self.render("templates/thread.html", thread=thread, board=board)

    def post(self, board, number):
        title = self.get_argument("title", None)
        text = self.get_argument("text", None)
        file_name = ''
        if 'image' in self.request.files:
            image_body = self.request.files['image'][0]['body']
            file_name = board + '_' + str(number) + '.jpg'
            img = open('static/images/' + file_name, 'wb')
            img.write(image_body)
        db.posts.insert({
            'text': text, 
            'title': title, 
            'thread': number, 
            'number': max_number(),
            'image': file_name})
        self.redirect("/"+ board + "/" + number)



def max_number():
    try:
        post_number = db.posts.find().sort('number', -1).limit(1)[0]['number']
    except (IndexError):
        post_number = 0
    try:
        thread_number = db.threads.find().sort('number', -1).limit(1)[0]['number']
    except (IndexError):
        thread_number = 0
    return max(post_number, thread_number) + 1


application = tornado.web.Application([
    (r"^/", MainHandler),
    (r"^/([a-z]+)/", BoardHandler),
    (r"/([a-z]+)/(\d+)", ThreadHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"},),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
