#coding=utf-8

import os
import sys

startfrom = "KrnKml.3928"
go = False

sys.path = ["/home/s/smartru/django13"] + sys.path

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import SearchApp
from SearchApp.models import Word, Manuscript

import xml.dom, xml.dom.minidom

doc = xml.dom.minidom.parse("KrnKml.xml")

mscript = Manuscript.objects.get(pk = 1)


doc.normalize()

div1Els = doc.getElementsByTagName("div1")

for div1 in div1Els:
	part = int(div1.getAttribute("n"))
	div2Els = div1.getElementsByTagName("div2")
	for div2 in div2Els:
		page = int(div2.getAttribute("n"))
		div3Els = div2.getElementsByTagName("div3")
		for div3 in div3Els:
			front = (div3.getAttribute("type") == "front")
			div4Els = div3.getElementsByTagName("div4")
			for div4 in div4Els:
				column = int(div4.getAttribute("n"))
				lEls = div4.getElementsByTagName("l")
				for l in lEls:
					line = int(l.getAttribute("n"))
					positioninline = 1
					childEls = [el for el in l.childNodes if isinstance(el, xml.dom.minidom.Element)]
					for ce in childEls:
						word = Word()
						word.positioninline = positioninline
						positioninline += 1
						word.line = line
						word.page = page
						word.column = column
						word.part = part
						word.front = front
						word.manuscript = mscript
						if ce.tagName in (u"w", u"name", u"add", u"num"):
							if ce.tagName != "w": ce = ce.getElementsByTagName("w")[0]
							word.id = ce.getAttribute("xml:id")
							orig = ce.getElementsByTagName('orig')[0]
							if len(orig.getElementsByTagName('sic')) > 0:
								word.sic = True
								word.orig = orig.getElementsByTagName('sic')[0].toxml()[5:-6]
								if len(orig.getElementsByTagName('corr')) > 0:
									word.corr = orig.getElementsByTagName('corr')[0].toxml()[6:-7]
							else:			
								word.orig = ce.getElementsByTagName('orig')[0].toxml()[6:-7]
							if ce.parentNode.tagName == 'name': word.name = True
							if ce.parentNode.tagName == 'add': word.add = True
							if ce.parentNode.tagName == 'num':
								word.value = int(ce.parentNode.getAttribute("value"))
								word.num = True
							word.reg = ce.getElementsByTagName('reg')[0].toxml()[5:-6]
							word.src = ce.getElementsByTagName('src')[0].toxml()[5:-6]
						elif ce.tagName == u"c":
							word.id = ce.getAttribute("xml:id")
							word.orig = ce.childNodes[0].data
							word.src = ce.childNodes[0].data
							word.reg = ce.childNodes[0].data
							word.isPunctuation = True
						else:
							print "Unexpected xml: " + ce.toxml()
						
						word.save()
						print word.id
