# from django.urls import path
# from .views import SearchView

# urlpatterns = [
#     path('', SearchView.as_view(), name='search'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.SearchView.as_view(), name='search'),
    path('advanced/', views.AdvancedSearchView.as_view(), name='advanced-search'),
]