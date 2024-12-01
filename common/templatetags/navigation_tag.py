import re
import sys

from django.core.exceptions import ImproperlyConfigured
from django.template import Library, Node, TemplateSyntaxError, Variable
from django.template.base import VariableDoesNotExist
from django.utils.safestring import mark_safe
from django.conf import settings
from django.urls import resolve

from config.casbin import check_perm, check_str_perm


register = Library()


def match_path(match, path):
    if re.search(match, path):
        return True
    return False


class Navigation(Node):
    def __init__(self, nav_name, nav_variable, variables={}):
        self.nav_variable = nav_variable
        self.nav_name = nav_name

        try:
            NAVIGATION_CONF = getattr(settings, 'NAVIGATION_CONF')
        except AttributeError:
            raise ImproperlyConfigured('Navigation application requires configuring NAVIGATION_CONF setting.')
        __import__(NAVIGATION_CONF)
        self.navigation =  sys.modules[NAVIGATION_CONF]

        self.variables = {}
        for object in variables:
            self.variables[object] = Variable(variables[object])


    def render(self, context):
        objects = {}
        for object in self.variables:
            try:
                objects[object] = self.variables[object].resolve(context)
            except VariableDoesNotExist as e:
                objects[object] = str(self.variables[object])
        level = getattr(self.navigation, self.nav_name)
        if hasattr(level, '__call__'):
            level = level(context, objects)
        context[self.nav_variable] = self.get_nav_level(level, context)
        return ''


    def get_nav_level(self, level, context):
        user = context['request'].user
        ret = []
        for node in level:
            if ('logged' in node) and (node['logged'] is not None):
                if (node['logged'] is True) and (not user.is_authenticated):
                    continue
                elif (node['logged'] is False) and (user.is_authenticated):
                    continue

            if ('perms' in node) and node['perms']:
                if not check_str_perm(user, node['perms']):
                    continue
            else:
                url = node['url']
                if url == '':
                    url = '/'
                elif re.match(r'^.*?#$', url):
                    url = re.sub(r'#$', '', url)
                url_info = resolve(url)
                if url_info.namespace:
                    if not check_perm(user, url_info.namespace, url_info.url_name):
                        continue
                else:
                    if not check_perm(user, url_info.url_name):
                        continue

            if not ('match' in node) or node['match'] is None:
                node['match'] = r'^' + node['url'] + r'$'
            node['selected'] = match_path(node['match'], context['request'].path)

            if ('data' in node) and node['data']:
                node['data_attrs_str'] = mark_safe(' '.join(['%s="%s"' % (key, val) for key, val in node['data'].items()]))

            if ('sub' in node) and (not node['sub'] == None):
                sub_level = self.get_nav_level(node['sub'], context)
                if len(sub_level) > 0:
                    node['sub'] = sub_level
                else:
                    node['sub'] = None

            if ('sub' in node) and (node['sub'] is None) and re.match(r"^.*#$", node['url']):
                continue
            
            ret.append(node)

        return ret


    @classmethod
    def tag(cls, parser, token):
        bits = list(token.split_contents())
        tag_name = bits.pop(0)
        nav_name = bits.pop(0)
        nav_variable = nav_name
        variables = {}
        if bits:
            bit = bits.pop(0)
            if bit == 'as':
                try:
                    nav_variable = bits.pop(0)
                except IndexError:
                    raise TemplateSyntaxError("%r tag requires a variable name after 'as' statement" % tag_name)
                bit = None
                try:
                    bit = bits.pop(0)
                except IndexError:
                    pass

            if bit == 'with':
                while 1 :
                    try:
                        bit = bits.pop(0)
                    except IndexError:
                        break
                    try:
                        variable_name, variable_value = bit.split('=')
                        variables[variable_name] = variable_value
                    except:
                        raise TemplateSyntaxError("%r tag requires a name=value pairs after 'with' statement" % tag_name)
            elif bit is not None:
                raise TemplateSyntaxError("%r tag syntax error, 'as' or 'with' expected." % tag_name)
        return cls(nav_name, nav_variable, variables)

get_nav = register.tag('get_nav', Navigation.tag)