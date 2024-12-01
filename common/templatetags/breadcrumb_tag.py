from django import template
from django.template import Node, Variable
from django.template import VariableDoesNotExist

from config.casbin import check_perm as casbin_check_perm

register = template.Library()


@register.tag
def breadcrumb(parser, token):
	return Breadcrumbs(token.split_contents()[1:])


class Breadcrumbs(Node):
	def __init__(self, vars):
		self.vars = list(map(Variable, vars))


	def render(self, context):
		user = context['request'].user
		title = self.vars[0].var
		
		if (title.find("'") == -1) and (title.find('"') == -1):
			try:
				val = self.vars[0]
				title = val.resolve(context)
			except:
				title = ''
		else:
			title = title.strip("'").strip('"')

		url = None
		
		if len(self.vars) > 1:
			val = self.vars[1]
			try:
				url = val.resolve(context)
			except VariableDoesNotExist:
				url = None

		if url and not casbin_check_perm(user, url):
			url = None

		return create_crumb(title, url)


def create_crumb(title, url=None, css_class=None):
	if not css_class:
		css_class = 'link-secondary'
	if url:
		crumb = '<li class="breadcrumb-item small"><a class="%s" href="%s">%s</a></li>' % (css_class, url, title) 
	else:
		crumb = "<li class='breadcrumb-item small active' aria-current='page'>%s</li>" % (title)

	return crumb