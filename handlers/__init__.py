from . import admin, autoreply_handler, start


def register_handlers(app):
    start.register(app)
    admin.register(app)
    autoreply_handler.register(app)
