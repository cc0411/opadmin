from .models import Documents
from .forms import DocumentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View,UpdateView,CreateView,DeleteView,TemplateView,DetailView
from django.shortcuts import render,redirect,HttpResponse
from pure_pagination import PageNotAnInteger,EmptyPage,Paginator
import markdown
from django.core.urlresolvers import reverse_lazy
import logging
logger = logging.getLogger(__name__)
# Create your views here.

class DocListView(LoginRequiredMixin,ListView):
    template_name = 'wiki/doc.html'
    model = Documents
    context_object_name = 'all_docs'
    queryset = Documents.objects.all()
    ordering = ('-id')

    def get_queryset(self):
        self.queryset = super().get_queryset()
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(self.queryset, 10, request=self.request)
        self.queryset = p.page(page)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(DocListView, self).get_context_data()
        context['title'] = '文档列表'
        return context

class DocDetailView(LoginRequiredMixin,DetailView):
    model = Documents
    template_name = 'wiki/doc_detail.html'
    context_object_name =  '文章详情'
    def get_object(self, queryset=None):
        obj = super(DocDetailView,self).get_object()
        obj.content = markdown.markdown(obj.content.replace("\r\n", '  \n'),extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ],safe_mode=True,enable_attributes=False)
        return obj


class DocAddView(LoginRequiredMixin,CreateView):
    '''文档添加'''
    model = Documents
    form_class = DocumentForm
    template_name =  'user/change.html'
    success_url = reverse_lazy('wiki:doc_list')
    def get_context_data(self, **kwargs):
        context = super(DocAddView,self).get_context_data()
        context['title'] = '新增文档'
        return  context
    def get_initial(self):
        initial = super(DocAddView, self).get_initial()
        initial['author'] = self.request.user.name
        return initial
    def get_form(self, form_class=None):
        form = super(DocAddView, self).get_form(form_class)
        form.fields['author'].widget.attrs.update({'readonly': True})
        return form
class DocUpdateView(LoginRequiredMixin,UpdateView):
    '''文档修改'''
    model = Documents
    form_class = DocumentForm
    template_name = 'user/change.html'
    success_url = reverse_lazy('wiki:doc_list')
    def get_context_data(self, **kwargs):
        context = super(DocUpdateView,self).get_context_data()
        context['title'] = '更新文档'
        return  context
    def get_form(self, form_class=None):
        form = super(DocUpdateView, self).get_form(form_class)
        form.fields['author'].widget.attrs.update({'readonly': True})
        return form
class DocDelView(LoginRequiredMixin,DeleteView):

    '''文档删除'''
    model = Documents
    template_name = 'user/delete.html'
    success_url = reverse_lazy('wiki:doc_list')
    raise_exception = True
    def get_context_data(self, **kwargs):
        context = super(DocDelView,self).get_context_data()
        context['cancel'] = reverse_lazy('wiki:doc_list')
        context['title'] = '删除文档'
        return  context