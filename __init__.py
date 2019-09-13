#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

# The class that all Interface Action plugin wrappers must inherit from
from calibre.customize import InterfaceActionBase

class ScrambleEbookActionBase(InterfaceActionBase):
    '''
    This class is a simple wrapper that provides information about the actual
    plugin class. The actual interface plugin class is called InterfacePlugin
    and is defined in the action.py file, as specified in the actual_plugin field
    below.

    The reason for having two classes is that it allows the command line
    calibre utilities to run without needing to load the GUI libraries.
    '''
    name                = 'ScrambleEbook'
    description         = 'Create a copyright-safe scrambled copy of an ebook for debugging purposes'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'jackie_w'
    version             = (0, 0, 10)
    minimum_calibre_version = (3, 41, 0)

    #: This field defines the GUI plugin class that contains all the code
    #: that actually does something. Its format is module_path:class_name
    #: The specified class must be defined in the specified module.
    actual_plugin       = 'calibre_plugins.scrambleebook_plugin.uiaction:ScrambleEbookUiAction'

    def is_customizable(self):
        ''' This method must return True to enable customization via
        Preferences->Plugins  '''
        return False
