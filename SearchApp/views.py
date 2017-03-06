#coding=utf-8
# Create your views here.
import re
from itertools import groupby

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.paginator import Paginator, InvalidPage
from django import forms
from django.template import RequestContext
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_control

import utils
from models import Word, Manuscript, GramInfo
from utils import getNextWord, InconsistentGramDataException, replaceCharsByDict



def showLineForWordHelper(word):
	return Word.objects.filter(line = word.line, column = word.column,
		page = word.page, part = word.part, front = word.front,
		manuscript = word.manuscript).order_by('positioninline')

def showLineForWord(request, word_id):
	word = get_object_or_404(Word, pk = word_id)
	line = showLineForWordHelper(word)
	nextword = Word.objects.filter(id__gt = line.reverse()[0].id)[0]
	lines = [line, showLineForWordHelper(nextword)]
	
	return render_to_response('SearchApp/ShowLines.html', {'lines': lines})  

@cache_control(must_revalidate=False, max_age=3600)
def showManuscriptPage(request, man_slug, page_number, back):
	curword = request.GET.get("hghlt", None)		
	manuscript = get_object_or_404(Manuscript, slug = man_slug)
	word = get_list_or_404(Word, manuscript=manuscript, page=int(page_number), front= not bool(back))[0]
	wordsonpage = list(Word.objects.filter(page = word.page, part = word.part, front = word.front,
		manuscript = word.manuscript).order_by('column', 'line', 'positioninline'))
	columns = [list(g) for k, g in groupby(wordsonpage, lambda w: w.column)]
	for i in range(len(columns)):
		columns[i] = [list(g) for k, g in groupby(columns[i], lambda w: w.line)]
	for col in columns:
		for i in range(len(col)):
			line = col[i]
			if ("<lb/>" not in line[-1].orig) or ((len(col) > i + 2) and (col[i+1][0].line - line[-1].line > 1)):
				line[-1].orig = line[-1].orig + "<lb/>"
	nextword = getNextWord(wordsonpage[-1], quiet=True)
	nextPageLink = _getPageLinkForWord(nextword) if nextword else None
	prevword = getNextWord(wordsonpage[0], quiet=True, reverse=True)
	prevPageLink = _getPageLinkForWord(prevword) if prevword else None
	return render_to_response('SearchApp/ShowPage.html', {'columns': columns, 'curword': curword,
		'prevLink': prevPageLink, 'nextLink': nextPageLink})  

def _getPageLinkForWord(word):
	kwargs={"man_slug": word.manuscript.slug, "page_number": word.page}
	back = "" if word.front else "b"
	url = reverse("scat-show-page", kwargs={"man_slug": word.manuscript.slug,
		"page_number": word.page, "back": back})
	return url

def showWordPage(request, word_id):
	word = get_object_or_404(Word, pk = word_id)
	url = _getPageLinkForWord(word) + "?hghlt=" + word.id
	return HttpResponseRedirect(url)


class SearchForm(forms.Form):
	reg = forms.CharField(label = u"Слово", required = False)
	regsearchtype = forms.ChoiceField(label = u"Тип поиска", choices = 
		(("inclusion", u"Вхождение"), ("beginning", u"Начало"), ("end", u"Конец"), ("strict", u"Точное совпадение")),
		required = True
		)
	group = forms.BooleanField(label = "Группировать слова (альфа-версия)", required = False)
	manuscript = forms.ModelChoiceField(label = u"Рукопись", queryset=Manuscript.objects.all().order_by("name"), required = False)
	line = forms.IntegerField(label = u"Номер строки", min_value = 1, required = False)
	column = forms.IntegerField(label = u"Номер колонки", min_value = 1, required = False)
	page = forms.IntegerField(label = u"Номер страницы", min_value = 1, required = False)
	front = forms.NullBooleanField(label = u"Оборотная сторона", required = False)
	part = forms.IntegerField(label = u"Номер части", min_value = 1, required = False)
	sic = forms.NullBooleanField(label = u"Неправильное написание", required = False)
	add = forms.NullBooleanField(label = u"Вставка с полей", required = False)
	name = forms.NullBooleanField(label = u"Имя собственное", required = False)
	num = forms.NullBooleanField(label = u"Является числом", required = False)

class GramInfoSearchForm(forms.ModelForm):
	class Meta:
		model = GramInfo
		exclude = ("word", )

@cache_control(must_revalidate=False, max_age=3600)
def search(request):
	manuscripts = Manuscript.objects.all().order_by("name")
	results = ""
	nextPageUrl = ""
	prevPageUrl = ""
	firstObject = ""
	if request.GET:
		wordForm = SearchForm(request.GET)
		gramForm = GramInfoSearchForm(request.GET)
		if wordForm.is_valid() and gramForm.is_valid():
			words = Word.objects.filter(isPunctuation = False)
			if (wordForm.cleaned_data["sic"] is not None): words = words.filter(sic = wordForm.cleaned_data["sic"])
			if (wordForm.cleaned_data["add"] is not None): words = words.filter(add = wordForm.cleaned_data["add"])
			if (wordForm.cleaned_data["name"] is not None): words = words.filter(name = wordForm.cleaned_data["name"])
			if (wordForm.cleaned_data["num"] is not None): words = words.filter(num = wordForm.cleaned_data["num"])
			if (wordForm.cleaned_data["front"] is not None): words = words.filter(front = wordForm.cleaned_data["front"])
			if wordForm.cleaned_data["line"]: words = words.filter(line = wordForm.cleaned_data["line"])
			if wordForm.cleaned_data["column"]: words = words.filter(column = wordForm.cleaned_data["column"])
			if wordForm.cleaned_data["manuscript"]: words = words.filter(manuscript = wordForm.cleaned_data["manuscript"])
			if wordForm.cleaned_data["page"]: words = words.filter(page = wordForm.cleaned_data["page"])
			if wordForm.cleaned_data["part"]: words = words.filter(part = wordForm.cleaned_data["part"])
			if wordForm.cleaned_data["reg"]:
				if wordForm.cleaned_data["regsearchtype"] == "inclusion":
					words = words.filter(reg__contains = wordForm.cleaned_data["reg"].upper())
				elif wordForm.cleaned_data["regsearchtype"] == "beginning":
					words = words.filter(reg__startswith = wordForm.cleaned_data["reg"].upper())
				elif wordForm.cleaned_data["regsearchtype"] == "end":
					words = words.filter(reg__endswith = wordForm.cleaned_data["reg"].upper())
				elif wordForm.cleaned_data["regsearchtype"] == "strict":
					words = words.filter(reg__exact = wordForm.cleaned_data["reg"].upper())
			gramInfoDictForFilter = {}
			for item in gramForm.cleaned_data.iteritems():
				if item[1] is not None:
					gramInfoDictForFilter["gramInfo__" + item[0]] = item[1]
			words = words.filter(**gramInfoDictForFilter)
			if wordForm.cleaned_data["group"]:
				words = words.order_by("orig")
			
			p = Paginator(words, 30, orphans = 6)
			try:
				page = p.page(request.GET["p"])
			except InvalidPage:
				page = p.page(p.num_pages)
			words = page.object_list
			results = []
			for word in words:
				results += [{"orig": word.orig, "id": word.id, "line": Word.objects.filter(page=word.page, part=word.part, front=word.front,
					manuscript=word.manuscript, column=word.column, line=word.line).order_by('positioninline')}]

			if page.has_next():
				nextPageUrl = re.sub(r"(&|\?)p=[^&]*", r"\1p=" + str(page.next_page_number()), request.get_full_path())
			if page.has_previous():
				prevPageUrl = re.sub(r"(&|\?)p=[^&]*", r"\1p=" + str(page.previous_page_number()), request.get_full_path())
			firstObject = page.start_index()
	else:
		wordForm = SearchForm()
		gramForm = GramInfoSearchForm()
		
	return render_to_response('SearchApp/Search.html', {'results': results, 'pagination': (prevPageUrl, nextPageUrl, firstObject), 'wordForm': wordForm,
	'gramForm': gramForm, 'alwaysShow': ("reg", "regsearchtype",)})
	
class GramDataUploadForm(forms.Form):
	manuscript = forms.ModelChoiceField(label = "Рукопись", queryset=Manuscript.objects.all().order_by("name"))
	firstwordid = forms.CharField(label = "ID первого слова")
	csv = forms.FileField(label = "Файл данных")

@transaction.commit_on_success
def uploadManuscript(request):
	if request.POST:
		form = GramDataUploadForm(request.POST, request.FILES)
		if form.is_valid():
			utils.ParseXMLIntoDB(form.cleaned_data['csv'], form.cleaned_data['manuscript'])
	else:
		form = GramDataUploadForm()
		
	return render_to_response('SearchApp/uploadGramData.html', {'form': form}, context_instance=RequestContext(request))

@transaction.commit_on_success
def uploadGramData(request):
	if request.POST:
		form = GramDataUploadForm(request.POST, request.FILES)
		if form.is_valid():
			word = Word.objects.get(pk = form.cleaned_data['firstwordid'])
			for line in form.cleaned_data['csv'].readlines():
				orl = line
				if len(line) > 10:
					line = line.rstrip("\r\n").replace(" ","")
					line = line.decode('utf-8').split(';')
					if line[0] == u"skip":
						word = getNextWord(word, allowPunctuation=False)
						continue
					src = word.src.replace("&amp;", "&").replace("&lt;","<").replace("&gt;",">").replace(" ", "").strip("&.,\"")
					line[0] = line[0].strip("&.,\"")
					line[0] = replaceCharsByDict(line[0],u'ETOPAHKXCBMeopaxcy',u'ЕТОРАНКХСВМеорахсу')
					if line[0] != src: raise InconsistentGramDataException(line[0] + u" != " + src + " (" + word.id + ")" + repr(orl))
					utils.generateGramData(line, word)
					word = getNextWord(word, allowPunctuation=False)
	else:
		form = GramDataUploadForm()
		
	return render_to_response('SearchApp/uploadGramData.html', {'form': form}, context_instance=RequestContext(request))
