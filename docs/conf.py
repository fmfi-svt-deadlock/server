#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

from recommonmark.parser import CommonMarkParser
import sphinx_rtd_theme

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
]

# autodoc needs to be able to find deadlock stuff
sys.path.insert(0, os.path.abspath(os.path.pardir))

templates_path = ['_templates']

source_suffix = ['.rst', '.md']
source_parsers = {
    '.md': CommonMarkParser,
}

master_doc = 'index'

project = 'Deadlock/Server'
copyright = u'2016, FMFI ŠVT'
author = u'FMFI ŠVT'

# The short X.Y version.
version = '0.1'
# The full version, including alpha/beta/rc tags.
release = '0.1'

exclude_patterns = ['_build']

# -- Options for HTML output ----------------------------------------------

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The empty string is equivalent to '%b %d, %Y'.
html_last_updated_fmt = ''

html_use_smartypants = True
