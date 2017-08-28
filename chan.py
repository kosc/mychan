#!/usr/bin/env python3.2
from pymongo import MongoClient
import tornado.web
from tornado.web import RequestHandler
import tornado.template

client = MongoClient()
db = client.chandb


class MainHandler(RequestHandler):

    def get(self):
        boards = db.boards.find({}, {'name': 1, 'desc': 1})
        args = {'boards': boards}
        title = 'Main page'
        self.render("templates/layout.html",
                    args=args,
                    page='index.html',
                    title=title)


class BoardHandler(RequestHandler):

    def get(self, brd):
        board = db.boards.find_one({'name': brd})
        threads = db.posts.find({'board': brd, 'parent_id': 0})
        args = {'board': board, 'threads': threads}
        title = brd + ' - Threads'
        self.render("templates/layout.html",
                    args=args,
                    page='board.html',
                    title=title)

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
        db.posts.insert({
            'board': board,
            'number': int(number),
            'title': title,
            'text': message,
            'image': file_name,
            'parent_id': 0})
        self.redirect("/" + board + "/")


class ThreadHandler(RequestHandler):

    def get(self, board, number):
        thread = list(db.posts.find({'number': int(number)}))
        posts = list(db.posts.find({'parent_id': int(number)}))
        thread += posts
        args = {'thread': thread, 'board': board}
        title = board + ' - Thread #' + str(number)
        self.render("templates/layout.html",
                    args=args,
                    page='thread.html',
                    title=title)

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
            'parent_id': int(number),
            'number': max_number(),
            'image': file_name})
        self.redirect("/" + board + "/" + number)


def max_number():
    try:
        post_number = db.posts.find().sort('number', -1).limit(1)[0]['number']
    except (IndexError):
        post_number = 0
    return post_number + 1


application = tornado.web.Application([
    (r"^/", MainHandler),
    (r"^/([a-z]+)/", BoardHandler),
    (r"/([a-z]+)/(\d+)", ThreadHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"},),
])

if __name__ == "__main__":
    PORT = 8888
    application.listen(PORT)
    print("Dev server is running on http://127.0.0.1:{}/".format(PORT))
    print("Press Ctrl-C to stop.")
    tornado.ioloop.IOLoop.instance().start()
