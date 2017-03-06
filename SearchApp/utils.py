#coding=utf-8
from models import Word, GramInfo, corrGramInfo
from django.core.exceptions import ObjectDoesNotExist
import re
import xml.dom, xml.dom.minidom

class InconsistentGramDataException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

def getNextWord(word, allowPunctuation=True, reverse=False, quiet=False):
	m = re.match(r"^(.+)\.(\d+)$", word.id)
	i = 1
	maxretries = 5
	k = 1 if not reverse else -1
	while (i < maxretries):
		wid = m.group(1) + "." + unicode(int(m.group(2)) + i*k)
		q = Word.objects.filter(pk = wid)
		if q and (allowPunctuation or not q[0].isPunctuation): return q[0]
		i += 1
	if not quiet: raise ObjectDoesNotExist

def replaceCharsByDict(unistr, frm, to):
    if len(frm) != len(to): raise "frm != to"
    result = list(unistr)
    for i in range(len(result)):
        if result[i] in frm: result[i] = to[frm.index(result[i])]
    return u''.join(char for char in result)

def generateGramData(gramDataCSV, word):
	g = GramInfo()
	g.word = word
	corrg = corrGramInfo()
	corrg.word = word
	corrg.used = False
		
		
	def setGramAttribute(attrname, data, gramdict):
		#Sets grammatical attribute for both GramInfo and corrGramInfo
		if data == u"вин/род":
			# Animate is a special case
			g.animate = True
			g.case = 4
			return
		data = data.replace(u"а/имп", u"а%имп").replace(u"р/скл", u"р%скл").replace(u"н/б",u"н%б")
		dataspl = data.split("/")
		try:
			setattr(g, attrname, gramdict[dataspl[0]])
			if len(dataspl) > 1:
				setattr(corrg, attrname, gramdict[dataspl[1]])
				corrg.used = True
		except KeyError:
			raise InconsistentGramDataException("Invalid %s: %s (word %s)" % (attrname, data, word.src))
		
	dTypes = {"a": 1, "ja": 2, "o":3, "jo":4, "u":5, u"i": 6, "en": 7, "men": 8, "es": 9, "ent": 10,
		"er":11, "uu": 12, u"личн": 13, u"м": 14, u"тв": 15, u"р%скл": 16}
	cases = {u"им": 1, u"род": 2, u"дат": 3, u"вин": 4, u"тв": 5, u"мест": 6, u"зв": 7}
	verbTenses = {u"н%б": 1, u"аорпр": 2, u"аорсигм": 3, u"аоргл": 4, u"аорнов": 5, u"а%имп": 6, u"имп": 7,
		u"перф": 8,	u"плюскв": 9, u"буд": 10, u"буд1": 11, u"буд2": 12,	u"прош": 13}
	numbers = {u"ед": 1, u"дв": 2, u"мн": 3, u"0": 0}
	persons = {u"1": 1, u"2": 2, u"3": 3}
	verbClasses = {u"1": 1, u"2": 2, u"3": 3, u"4": 4, u"5": 5}
	verbRoles = {u"св": 1, u"пр-св": 2,	u"пр": 3, u"инф": 4}
	genders = {u"м": 1,	u"ж": 2, u"ср": 3, u"0": 0}
	participleTenses = {u"наст": 1,	u"прош": 2}
	moods = {u"изъяв": 1, u"повел": 2, u"сосл": 3}
		

	def NounAdjNum():
		gramDataCSV[2] = replaceCharsByDict(gramDataCSV[2],u'ао', u'ao')
		setGramAttribute("declensionType", gramDataCSV[2], dTypes)
		setGramAttribute("case", gramDataCSV[3], cases)
		setGramAttribute("number", gramDataCSV[4], numbers)
		setGramAttribute("gender", gramDataCSV[5], genders)
		
	def Particip():
		gramDataCSV[2] = replaceCharsByDict(gramDataCSV[2],u'ао', u'ao')
		setGramAttribute("declensionType", gramDataCSV[2], dTypes)
		setGramAttribute("participleTense", gramDataCSV[3], participleTenses)
		setGramAttribute("case", gramDataCSV[4], cases)
		setGramAttribute("number", gramDataCSV[5], numbers)
		setGramAttribute("gender", gramDataCSV[6], genders)
		
	def Verb():
		setGramAttribute("mood", gramDataCSV[2], moods)
		if g.mood == 1:
			setGramAttribute("verbTense", gramDataCSV[3], verbTenses)
			if g.verbTense in range(2,8) or g.verbTense == 10:
				setGramAttribute("person", gramDataCSV[4], persons)
				setGramAttribute("number", gramDataCSV[5], numbers)
			elif g.verbTense == 13:
				setGramAttribute("gender", gramDataCSV[4], genders)
				setGramAttribute("number", gramDataCSV[5], numbers)
			elif g.verbTense == 1:
				setGramAttribute("person", gramDataCSV[4], persons)
				setGramAttribute("number", gramDataCSV[5], numbers)
				setGramAttribute("verbClass", gramDataCSV[6], verbClasses)
			else:
				setGramAttribute("verbRole", gramDataCSV[6], verbRoles)
				if g.verbRole == 1:
					setGramAttribute("person", gramDataCSV[4], persons)
					setGramAttribute("number", gramDataCSV[5], numbers)
				if g.verbRole in (2,3):
					setGramAttribute("gender", gramDataCSV[4], genders)
					setGramAttribute("number", gramDataCSV[5], numbers)
				if g.verbRole == 4:
					pass #it's infinitive, we already have everything needed
		elif g.mood == 2:
			# imperative
			setGramAttribute("person", gramDataCSV[3], persons)
			setGramAttribute("number", gramDataCSV[4], numbers)
			setGramAttribute("verbClass", gramDataCSV[5], verbClasses)
		elif g.mood == 3:
			#subjunctive
			setGramAttribute("verbRole", gramDataCSV[5], verbRoles)
			if g.verbRole == 1:
				setGramAttribute("person", gramDataCSV[3], persons)
				setGramAttribute("number", gramDataCSV[4], numbers)
			if g.verbRole == 3:
				setGramAttribute("gender", gramDataCSV[3], genders)
				setGramAttribute("number", gramDataCSV[4], numbers)
			
	
	if gramDataCSV[1] == u"сущ":
		g.POS = 1
		NounAdjNum()
	elif gramDataCSV[1] == u"мест":
		g.POS = 2
		gramDataCSV[2] = replaceCharsByDict(gramDataCSV[2],u'ао', u'ao')
		setGramAttribute("declensionType", gramDataCSV[2], dTypes)
		if g.declensionType == 13:
			if gramDataCSV[3] == u"возвр":
				g.reflexive = True
				setGramAttribute("case", gramDataCSV[4], cases)
			else:
				setGramAttribute("person", gramDataCSV[3], persons)
				setGramAttribute("case", gramDataCSV[4], cases)
				setGramAttribute("number", gramDataCSV[5], numbers)
		else:
			setGramAttribute("case", gramDataCSV[3], cases)
			setGramAttribute("number", gramDataCSV[4], numbers)
			setGramAttribute("gender", gramDataCSV[5], genders)
	elif gramDataCSV[1] == u"прил":
		g.POS = 3          
		NounAdjNum()
	elif gramDataCSV[1] == u"прил/ср":
		g.POS = 4  
		NounAdjNum()        
	elif gramDataCSV[1] == u"числ":
		g.POS = 5
		NounAdjNum()
	elif gramDataCSV[1] == u"числ/п":
		g.POS = 6        
		NounAdjNum()
	elif gramDataCSV[1] == u"прич":
		g.POS = 7  
		g.reflexive = False
		Particip()
	elif gramDataCSV[1] == u"прич/в":
		g.POS = 7
		g.reflexive = True
		Particip()
	elif gramDataCSV[1] == u"гл":
		g.POS = 8
		g.reflexive = False
		Verb()
	elif gramDataCSV[1] == u"гл/в":
		g.POS = 8
		g.reflexive = True
		Verb()
	elif gramDataCSV[1] == u"инф":
		g.POS = 9
		g.reflexive = False
	elif gramDataCSV[1] == u"инф/в":
		g.POS = 9
		g.reflexive = True
	elif gramDataCSV[1] == u"суп":
		g.POS = 10          
	elif gramDataCSV[1] == u"нар":
		g.POS = 11          
	elif gramDataCSV[1] == u"пред":
		g.POS = 12          
	elif gramDataCSV[1] == u"посл":
		g.POS = 13
	elif gramDataCSV[1] == u"союз":
		g.POS = 14          
	elif gramDataCSV[1] == u"част":
		g.POS = 15          
	elif gramDataCSV[1] == u"межд":
		g.POS = 16          
	else: raise InconsistentGramDataException("Invalid part of speech: '" + gramDataCSV[1] + "'")
	
	g.save()
	if corrg.used:
		corrg.save()
	else:
		corrg = corrGramInfo.objects.filter(pk = word)
		if corrg:
			corrg.delete()
			
			
def ParseXMLIntoDB(xmlfile, mscript):
	doc = xml.dom.minidom.parse(xmlfile)

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
	
