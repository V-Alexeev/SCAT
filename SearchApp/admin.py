from SearchApp.models import Word, Manuscript, GramInfo, corrGramInfo
from django.contrib import admin

class WordAdmin(admin.ModelAdmin):
	list_display = ('id', 'orig', 'reg', 'page', 'line', 'manuscript')
	
class ManuscriptAdmin(admin.ModelAdmin):
	list_display = ('name',)
	
class GramInfoAdmin(admin.ModelAdmin):
	list_display = ('word', 'POS', 'declensionType',  'gender', 'case', 'number', 'mood', 'verbTense', 'verbClass', 'verbRole', 'participleTense','person', 'reflexive')


admin.site.register(Word, WordAdmin)
admin.site.register(GramInfo, GramInfoAdmin)
admin.site.register(corrGramInfo, GramInfoAdmin)
admin.site.register(Manuscript, ManuscriptAdmin)
