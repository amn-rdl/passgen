from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="home"),
    path("tips/", views.tips, name="tips"),
    path("about/", views.about, name="about"),
    path("search/", views.search, name='search'),
    path("mypass/", views.mypass, name="mypass"),    
    path("login/", views.login_view, name="login"),
    path("signin/", views.signin_view, name="signin"), 
    path("logout/", views.logout_view, name="logout"),    
    path("myaccount/", views.myaccount, name="account"),
    path("no_result/", views.no_result, name='noresult'),
    path("change/", views.change_info, name='change_info'),
    path("edit_mdp/<site>/<username>/", views.edit_mdp, name="edit_mdp"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)