from __future__ import (unicode_literals, division, absolute_import, print_function)

def main(some_text):
    from PyQt5.Qt import QLabel
    from calibre.gui2 import Application
    app = Application([])

    w = QLabel(some_text)
    w.setMinimumHeight(100)
    w.setMinimumWidth(100)

    w.show()
    w.raise_()
    app.exec_()