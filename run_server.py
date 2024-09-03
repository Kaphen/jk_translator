from flask import Flask
from pywebio.platform.flask import webio_view

from server.api import bp
from server.gui import GUI

app = Flask(__name__)
app.register_blueprint(bp)
gui = GUI()
app.add_url_rule('/', 'webio_view', webio_view(gui.gui_index),
                     methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    app.run(port=8080, debug=True)
