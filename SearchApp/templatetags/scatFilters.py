#coding=utf-8
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from utils import shiftoverlines
from django import template

register = template.Library()

@register.filter
@stringfilter
def ScatWordFormat(inpt, nobr=False):
	try:
		word = inpt
		if nobr:
			word = word.replace("<lb/>","|")
		else:
			word = word.replace("<lb/>","<br/>")
		word = word.replace("<pb/>","|").replace("<cb/>","|")
		word = shiftoverlines(word)
		return mark_safe(word)
	except:
		return mark_safe(inpt)
	
