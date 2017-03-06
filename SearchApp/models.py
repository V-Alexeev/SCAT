#coding=utf-8
from django.db import models

GramPOS = (
	(1, "существительное"),
	(2, "местоимение"),
	(3, "прилагательное"),
	(4, "прил. сравнит. степени"),
	(5, "числительное количественное"),
	(6, "числительное порядковое"),
	(7, "причастие"),	
	(8, "глагол"),
	(9, "инфинитив"),
	(10, "супин"),
	(11, "наречие"),
	(12, "предлог"),
	(13, "послелог"),
	(14, "союз"),
	(15, "частица"),
	(16, "междометие")
	)

GramDeclensionTypes = (
		(1, "a"),
		(2, "ja"),
		(3, "o"),
		(4, "jo"),
		(5, u"ŭ"),
		(6, "i"),
		(7, u"en"),
		(8, u"men"),
		(9, "es"),
		(10, "ent"),
		(11, "er"),
		(12, u"ū"),
		(13, u"личное (1-2 лицо, возвр.)"),
		(14, u"местоим. мягкое"),
		(15, u"местоим. твёрдое"),
		(16, u"разносклоняемое")
	)

GramGenders = (
	(1, "м"),
	(2, "ж"),
	(3, "ср"),
	(0, "0")
	)

GramPersons = (
	(1, "1"),
	(2, "2"),
	(3, "3")
	)

GramVerbClasses = (
	(1, "1"),
	(2, "2"),
	(3, "3"),
	(4, "4"),
	(5, "5")
	)

GramVerbRoles = (
	(1, "связка"),
	(2, "причастие-связка"),
	(3, "причастие"),
	(4, "инфинитив")
	)

GramCases = (
	(1, "им"),
	(2, "род"),
	(3, "дат"),
	(4, "вин"),
	(5, "тв"),
	(6, "мест"),
	(7, "зв"),
	)

GramNumbers = (
	(1, "ед"),
	(2, "дв"),
	(3, "мн"),
	(0, "0")
	)

GramMoods = (
	(1, "изъяв"),
	(2, "повел"),
	(3, "сосл")
	)

GramVerbTenses = (
	(1, "наст/буд"),
	(2, "аорист простой"),
	(3, "аорист древн. сигм."),
	(4, "аорист от основы на гл."),
	(5, "аорист новый сигм."),
	(6, "аорист от основы имперфекта"),
	(7, "имперфект"),
	(8, "перфект"),
	(9, "плюсквамперфект"),
	(10, "будущее (гл. \"буду\""),
	(11, "будущее 1"),
	(12, "будущее 2"),
	(13, "простое прошедшее")
	)

GramParticipleTenses = (
	(1, "настоящее"),
	(2, "прошедшее")
	)


class Manuscript(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField()
	def __unicode__(self): return self.name

class Word(models.Model):
	orig = models.CharField(max_length=100, db_index = True)
	reg = models.CharField(max_length=100, db_index = True)
	src = models.CharField(max_length=100, db_index = True)
	id = models.CharField(max_length=100, primary_key = True, db_index = True)
	line = models.PositiveSmallIntegerField(db_index = True)
	column = models.PositiveSmallIntegerField(db_index = True)
	page = models.PositiveIntegerField(db_index = True)
	part = models.PositiveSmallIntegerField(db_index = True)
	front = models.BooleanField(db_index = True)
	manuscript = models.ForeignKey('Manuscript', related_name='words', on_delete = models.PROTECT, db_index = True)
	sic = models.BooleanField(default = False, db_index = True)
	corr = models.CharField(max_length=100, db_index = True, default = '', blank = True)
	add = models.BooleanField(default = False, db_index = True)
	name = models.BooleanField(default = False, db_index = True)
	num = models.BooleanField(default = False, db_index = True)
	value = models.IntegerField(db_index = True, null = True, blank = True)
	positioninline = models.PositiveSmallIntegerField(db_index = True)
	isPunctuation = models.BooleanField(default = False, db_index = True)
	def __unicode__(self): return self.src
	
class abstractGramInfo(models.Model):
	POS = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramPOS, verbose_name="Часть речи")
	declensionType = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramDeclensionTypes, verbose_name="Тип склонения")
	gender = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramGenders, verbose_name="Род")
	case = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramCases, verbose_name="Падеж")
	number = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramNumbers, verbose_name="Число")
	mood = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramMoods, verbose_name="Наклонение глагола")
	verbTense = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramVerbTenses, verbose_name="Время глагола")
	verbClass = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramVerbClasses, verbose_name="Класс глагола")
	verbRole = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramVerbRoles, verbose_name="Роль")
	participleTense = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramParticipleTenses, verbose_name="Время причастия")
	person = models.PositiveSmallIntegerField(db_index = True, null = True, blank = True, choices = GramPersons, verbose_name="Лицо")
	reflexive = models.NullBooleanField(db_index = True, null = True, blank = True, verbose_name="Возвратность")
	animate = models.NullBooleanField(db_index = True, null = True, blank = True, verbose_name="Одушевлённость")
	class Meta:
		abstract = True
	
class corrGramInfo(abstractGramInfo):
	word = models.OneToOneField("Word", primary_key = True, db_index = True, related_name = "corrGramInfo", editable = False)

class GramInfo(abstractGramInfo):
	word = models.OneToOneField("Word", primary_key = True, db_index = True, related_name = "gramInfo", editable = False)
