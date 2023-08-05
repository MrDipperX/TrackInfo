from .insert_db import upsert, from_xlsx_to_df, pstgr_engine

from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from datetime import datetime, timedelta
# from django.utils.translation import gettext

from .forms import LoginUserForm, SearchForm, ExcelFileForm
from .utils import DataMixin
from .models import PassengerTrack


class TrackHome(DataMixin, ListView):
    model = PassengerTrack
    template_name = 'track_manage/index.html'
    context_object_name = 'tracks'
    paginate_by = 30
    form = SearchForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return super(TrackHome, self).get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):

        val_dict = dict()
        if self.request.GET.get("search_input"):
            val_dict['search_input'] = self.request.GET['search_input']
        elif self.request.GET.get("type"):
            val_dict['type'] = self.request.GET['type']
        elif self.request.GET.get("model"):
            val_dict['model'] = self.request.GET['model']
        elif self.request.GET.get("state"):
            val_dict['state'] = self.request.GET['state']
        elif self.request.GET.get("all"):
            val_dict['all'] = self.request.GET['all']
        elif self.request.GET.get("review"):
            val_dict['all'] = self.request.GET['review']
        elif self.request.GET.get("change"):
            val_dict['all'] = self.request.GET['change']
        elif self.request.GET.get("repair"):
            val_dict['all'] = self.request.GET['repair']

        if self.request.GET.get("is_more_info"):
            self.request.session['is_more_info'] = True
        elif self.request.GET == {}:
            self.request.session['is_more_info'] = False

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Вагоны', request=self.request, search_form=self.form, val_dict=val_dict)

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        search_form = self.form(self.request.GET)
        queryset = ""
        if search_form.is_valid() and self.request.GET.get("search_input"):
            queryset = PassengerTrack.objects.filter(number=self.request.GET['search_input'])
        elif self.request.GET.get("type"):
            queryset = PassengerTrack.objects.filter(wagon_type__contains=self.request.GET['type'])
        elif self.request.GET.get("model"):
            queryset = PassengerTrack.objects.filter(wagon_model__contains=self.request.GET['model'])
        elif self.request.GET.get("state"):
            queryset = PassengerTrack.objects.filter(state_of_use__contains=self.request.GET['state'])
        elif self.request.GET.get("all"):
            queryset = PassengerTrack.objects.all()
        elif self.request.GET.get("change"):
            now = datetime.now() - timedelta(days=3650)
            queryset = PassengerTrack.objects.filter(last_kr_2__lte=now)
        elif self.request.GET.get("repair"):
            now = datetime.now() - timedelta(days=7300)
            queryset = PassengerTrack.objects.filter(last_kvr__lte=now)
        elif self.request.GET.get("review"):
            now = datetime.now() - timedelta(days=730)
            queryset = PassengerTrack.objects.filter(last_dr__lte=now)

        return queryset


# class TrackInsertView(DataMixin, TemplateView):
#     template_name = ''
#     form = ''


class TrackLogin(DataMixin, LoginView):
    template_name = 'track_manage/login.html'
    form_class = LoginUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Вход', request=self.request)

        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')


class TrackUploadFile(DataMixin, FormView):
    template_name = 'track_manage/upload.html'
    form_class = ExcelFileForm
    success_url = '../'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='File', request=self.request)

        return dict(list(context.items()) + list(c_def.items()))

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()

        form = self.get_form(form_class)

        file = request.FILES.get('file_input')

        if form.is_valid():
            if file.name.split(".")[1] in ['xlsx', 'xls']:
                print(upsert("track_manage_passengertrack", from_xlsx_to_df(file), pstgr_engine()))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def logout_user(request):
    logout(request)
    return redirect('home')


def page_not_found(request, exception):
    return HttpResponseNotFound(f"Страница не найдена!")
