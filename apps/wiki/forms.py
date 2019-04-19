# -*- coding:utf-8 -*-
from .models import Documents
from django import  forms
from django.forms import widgets
from  DjangoUeditor.widgets import UEditorWidget
from DjangoUeditor.forms import UEditorField
class DocumentForm(forms.ModelForm):
    author = forms.CharField(label='作者',widget=widgets.TextInput(attrs={'class':'form-control'}))
    title = forms.CharField(label='标题',max_length=128,widget=widgets.TextInput(attrs={'class':'form-control'}))
    content = UEditorField(label='内容',width=950,height=300, toolbars="full", imagePath="wiki/images/", filePath="wiki/files/",upload_settings={"imageMaxSize": 1204000}, settings={})
    class Meta:
        model = Documents
        fields = ['title','content','author']
