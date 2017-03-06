#coding=utf-8

import re

def insertspans(match):
	start = ''
	end = ''
	for char in match.group(0)[1:]:
		start += '<span class="second">'+ char + "&nbsp;"
		end +='</span>'
	return match.group(0)[0] + start + end

def shiftoverlines(text):
	text = text.lower()
	text = text.replace('<g ref="#i8-overline"/>',u'') #U+E042
	text = text.replace('<g ref="#i10-overline"/>',u'')  #U+E050
	text = text.replace('<g ref="#omega-overline"/>',u'') #U+E052
	text = text.replace('<g ref="#yeri-overline"/>',u'') #U+E04D
	text = text.replace('<g ref="#yer-overline"/>',u'') #U+E051
	text = text.replace('<g ref="#u-overline"/>',u'') #U+E049
	text = text.replace('<g ref="#ou-overline"/>',u'') #U+E04A
	return re.sub(u"(^[ⷠⷡⷢⷣⷤⷥⷦⷧⷨⷩⷪⷫⷬⷭⷮⷯⷰⷱⷲⷳⷴⷵⷶⷷⷸⷹⷺⷻⷼⷽⷾⷿ]+)|([ⷠⷡⷢⷣⷤⷥⷦⷧⷨⷩⷪⷫⷬⷭⷮⷯⷰⷱⷲⷳⷴⷵⷶⷷⷸⷹⷺⷻⷼⷽⷾⷿ]{2,})",insertspans,text)
