from pywebio.platform.flask import webio_view

from server.gui import GUI
from server.api import app


if __name__ == '__main__':
    gui = GUI()
    # api = API()
    app.add_url_rule('/', 'webio_view', webio_view(gui.gui_index),
                     methods=['GET', 'POST', 'OPTIONS'])
    app.run(port=8080, debug=True)