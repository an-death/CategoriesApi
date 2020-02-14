from django.urls import path

from . import views

urlpatterns = [
    path('', views.CategoriesList.as_view()),
    path('<int:pk>/', views.CategoryTree.as_view()),
]