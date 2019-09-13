#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

'''if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None'''

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction

# Get required support modules for all plugin actions
import os
try:
    from PyQt5.Qt import (QMenu, QToolButton,
        QDialog, QLabel, QDialogButtonBox,
        QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton)
except ImportError:
    from PyQt4.Qt import (QMenu, QToolButton,
        QDialog, QLabel, QDialogButtonBox,
        QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton)

from calibre.gui2 import error_dialog

#from calibre_plugins.scrambleebook_plugin.config import prefs
from calibre_plugins.scrambleebook_plugin.scrambleebook import (EbookScramble, get_fileparts)

OK_FORMATS = ('AZW3', 'EPUB', 'KEPUB')

class ScrambleEbookUiAction(InterfaceAction):
    name = 'ScrambleEbook'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.

    # Create our top-level menu/toolbar action (text, icon_path, tooltip, keyboard shortcut)
    ttip = 'Create a "scrambled text" external copy of a book\n(%s)\nCopyright-safe, for debugging purposes.' % ','.join(OK_FORMATS)
    action_spec = ('ScrambleEbook', None, _(ttip), ())
    action_type = 'current'

    #dont_add_to = frozenset(['context-menu-device', 'toolbar-device', 'menubar-device'])
    dont_add_to = frozenset([])
    dont_remove_from = frozenset([])
    #popup_type = QToolButton.MenuButtonPopup

    def genesis(self):
        # This method is called once per plugin, do initial setup here

        self.is_library_selected = True
        self.menu = QMenu(self.gui)

        # Set the icon for this interface action
        # The get_icons function is a builtin function defined for all your
        # plugin code. It loads icons from the plugin zip file. It returns
        # QIcon objects, if you want the actual data, use the analogous
        # get_resources builtin function.
        #
        # Note that if you are loading more than one icon, for performance, you
        # should pass a list of names to get_icons. In this case, get_icons
        # will return a dictionary mapping names to QIcons. Names that
        # are not found in the zip file will result in null QIcons.

        self.icons = get_icons(['images/plugin_icon.png',
                                'images/azw3.png',
                                'images/epub.png',
                                'images/kepub.png',
                                'images/azw3.svg',
                                'images/epub.svg',
                                'images/kepub.svg'])
        # The qaction is automatically created from the action_spec defined above
        #self.rebuild_menu()
        #self.qaction.setMenu(self.menu)
        self.qaction.setIcon(self.icons['images/plugin_icon.png'])
        self.qaction.triggered.connect(self.show_dialog)

    def location_selected(self, loc):
        self.is_library_selected = loc == 'library'

    '''def apply_settings(self):
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs, e.g. rebuild menus
        # prefs
        pass

    def library_changed(self, db):
        self.rebuild_menu()

    def rebuild_menu(self):
        m = self.menu
        m.clear()

    def show_configuration(self):
        self.interface_action_base_plugin.do_user_config(self.gui) '''

    def show_dialog(self):
        #base_plugin_object = self.interface_action_base_plugin
        #do_user_config = base_plugin_object.do_user_config

        class SelectedBookError(Exception): pass

        # Selected book checks. If error raise SelectedBookError
        # Get book from currently selected row. Only single row is valid
        try:
            rows = self.gui.current_view().selectionModel().selectedRows()

            if not rows or len(rows) == 0:
                errmsg = 'No book selected'
                raise SelectedBookError, errmsg

            if len(rows) > 1:
                errmsg = 'More than one book selected'
                raise SelectedBookError, errmsg

            if self.is_library_selected:
                # book is in calibre library
                #book_ids = list(map(self.gui.library_view.model().id, rows))
                book_ids = self.gui.library_view.get_selected_ids()
                book_id = book_ids[0]

                # check which formats exist and select one
                db = self.gui.current_db
                avail_fmts = db.new_api.formats(book_id, verify_formats=True)
                valid_fmts = [f for f in OK_FORMATS if f in avail_fmts]

                if len(valid_fmts) > 1:
                    seldlg = EbookSelectFormat(self.gui, valid_fmts, self.gui)
                    if seldlg.exec_():
                        valid_fmts = seldlg.result

                try:
                    fmt = valid_fmts[0]
                    path_to_ebook = db.new_api.format(book_id, fmt, as_path=True, preserve_filename=True)
                except:
                    path_to_ebook = None

                if not path_to_ebook:
                    errmsg = 'No %s available for this book' % ','.join(OK_FORMATS)
                    raise SelectedBookError, errmsg
            else:
                # book is on device
                paths = self.gui.current_view().model().paths(rows)
                path_to_ebook = paths[0]
                book_id = None

                x, x, ext, x = get_fileparts(path_to_ebook)
                if not ext.upper() in OK_FORMATS:
                    errmsg = 'Only books with file extensions %s are valid.\n\n' % ','.join(OK_FORMATS)
                    errmsg += '%s\nnot valid for this plugin' % path_to_ebook
                    raise SelectedBookError, errmsg

            # all OK, proceed with action
            dlg = EbookScramble(self.gui, path_to_ebook, book_id=book_id, from_calibre=True)
            dlg.exec_()

        except SelectedBookError as e:
            return error_dialog(self.gui, 'ScrambleEbook: Book selection error',
                                unicode(e), show=True)

class EbookSelectFormat(QDialog):
    # select a single format if >1 suitable to be scrambled
    def __init__(self, gui, formats, parent=None):
        QDialog.__init__(self, parent=parent)

        self.gui = gui
        self.formats = formats
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)

        msg = '\nThis book has multiple formats which could be scrambled.\n' \
            'Please select one of the following:\n'
        label = QLabel(msg)

        self.dradio = {}
        for k in self.formats:
            self.dradio[k] = QRadioButton(k)

        gpbox1 = QGroupBox('Formats available:')
        lay1 = QHBoxLayout()
        gpbox1.setLayout(lay1)

        for fmt in self.formats:
            lay1.addWidget(self.dradio[fmt])

        if 'EPUB' in self.formats:
            self.dradio['EPUB'].setChecked(True)
        else:
            self.dradio[self.formats[0]].setChecked(True)

        lay = QVBoxLayout()
        lay.addWidget(label)
        lay.addWidget(gpbox1)
        lay.addStretch()
        lay.addWidget(buttonBox)
        self.setLayout(lay)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle('ScrambleEbook: Select a single format')
        self.setWindowIcon(get_icons('images/plugin_icon.png'))

    @property
    def result(self):
        return tuple([k for k in self.formats if self.dradio[k].isChecked()])
