from __future__ import unicode_literals, print_function, absolute_import

from nose.tools import eq_
import tw2.core as twc

# copied from tw2.jquery
def request_local_tst():
    global _request_local, _request_id
#    if _request_id is None:
#        raise KeyError('must be in a request')
    if _request_local == None:
        _request_local = {}
    try:
        return _request_local[_request_id]
    except KeyError:
        rl_data = {}
        _request_local[_request_id] = rl_data
        return rl_data

twc.core.request_local = request_local_tst
_request_local = {}
_request_id = 'whatever'

def setUp():
    twc.core.request_local = request_local_tst
    twc.core.request_local()['middleware'] = twc.make_middleware()

def test_fontawesome_resource():
    from tw2.fontawesome import fontawesome_css
    the_link = "/resources/tw2.fontawesome/static/css/font-awesome.css"
    eq_(fontawesome_css.req().link, the_link)

def test_fontawesome_resource_min():
    from tw2.fontawesome import fontawesome_css
    fontawesome_css = fontawesome_css(variant='min')
    the_link = "/resources/tw2.fontawesome/static/css/font-awesome.min.css"
    eq_(fontawesome_css.req().link, the_link)

def test_fontawesome_external():
    from tw2.fontawesome import fontawesome_css
    from tw2.fontawesome.config import version
    fontawesome_css = fontawesome_css(external=True)
    the_link = (
        "//maxcdn.bootstrapcdn.com/font-awesome/%(version)s/css/"
        "font-awesome.css" % {'version': version})
    eq_(fontawesome_css.req().link, the_link)

def test_fontawesome_external_min():
    from tw2.fontawesome import fontawesome_css
    from tw2.fontawesome.config import version
    fontawesome_css = fontawesome_css(external=True, variant='min')
    the_link = (
        "//maxcdn.bootstrapcdn.com/font-awesome/%(version)s/css/"
        "font-awesome.min.css" % {'version': version})
    eq_(fontawesome_css.req().link, the_link)

def test_fontawesome_scriptname():
    twc.core.request_local()['middleware'] = twc.make_middleware(
            script_name='/foo')
    from tw2.fontawesome import fontawesome_css
    the_link = "/foo/resources/tw2.fontawesome/static/css/font-awesome.css"
    eq_(fontawesome_css.req().link, the_link)

def test_fontawesome_custom():
    from tw2.fontawesome import fontawesome_css
    fontawesome_css = fontawesome_css()
    the_link = "/foo/bar/fontawesome.css"
    fontawesome_css.link = the_link
    eq_(fontawesome_css.req().link, the_link)

def test_fontawesome_icon():
    from tw2.fontawesome import FontAwesomeIcon as icon
    eq_(icon.display(icon='home'), "<i class=\"fa fa-home\"></i>")
