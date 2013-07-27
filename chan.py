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
        try:
            post_number = db.posts.find().sort('number', -1).limit(1)[0]['number']
        except (IndexError):
            post_number = 0
        try:
            thread_number = db.threads.find().sort('number', -1).limit(1)[0]['number']
        except (IndexError):
            thread_number = 0
        number = max(post_number, thread_number) + 1
        db.threads.insert({'board': board, 'number': int(number), 'title': title, 'text': message})
        self.redirect("/" + board + "/")

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/([^/]+)/", BoardHandler)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
