"""Sphinx extension that embeds Disqus comments in documents.

https://readthedocs.org/projects/sphinxcontrib-disqus/
https://github.com/Robpol86/sphinxcontrib-disqus
https://pypi.python.org/pypi/sphinxcontrib-disqus
"""

from __future__ import print_function

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import ExtensionError

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '0.0.1'


class DisqusNode(nodes.General, nodes.Element):
    """Disqus <div /> node for Sphinx/docutils."""

    def __init__(self, disqus_identifier):
        """Store directive options during instantiation.

        :param str disqus_identifier: Unique identifier for each page where Disqus is present.
        """
        super(DisqusNode, self).__init__()
        self.disqus_identifier = disqus_identifier

    @staticmethod
    def visit(spht, node):
        """Append opening tags to document body list."""
        html_attrs = {
            'id': 'disqus_thread',
            'data-disqus-identifier': node.disqus_identifier or spht.page_name_todo_this,  # TODO or in directive.
        }
        spht.body.append(spht.starttag(node, 'div', '', **html_attrs))

    @staticmethod
    def depart(spht, _):
        """Append closing tags to document body list."""
        spht.body.append('</div>')


class DisqusDirective(Directive):
    """Disqus ".. disqus::" rst directive."""

    optional_arguments = 1
    option_spec = dict(disqus_identifier=str)

    def run(self):
        """Executed by Sphinx."""
        return [DisqusNode(self.options['disqus_identifier'])]


class EventHandlers(object):
    """Hold Sphinx event handlers as static methods."""

    @staticmethod
    def insert_javascript(app):
        """Insert Disqus read-only javascript into the document body during the builder-inited event.

        http://sphinx-doc.org/extdev/appapi.html#event-builder-inited
        From: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/mathjax.py

        :param app: Sphinx application object.
        """
        if not app.config.disqus_shortname:
            raise ExtensionError('disqus_shortname config value must be set for the disqus extension to work.')
        javascript = """\
            var disqus_shortname = '{shortname}';
            (function() {{
                var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
                dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
                (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
            }})();
        """.format(app.config.disqus_shortname)
        app.add_javascript(javascript)


def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('disqus_shortname', None, True)
    app.add_node(DisqusNode, html=(DisqusNode.visit, DisqusNode.depart))
    app.add_directive('disqus', DisqusDirective)
    app.connect('builder-inited', EventHandlers.insert_javascript)
    return dict(version=__version__)