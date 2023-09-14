from django.urls import path
from . import views


app_name = 'leads'
urlpatterns = [
    path('', views.LeadListView.as_view(), name='lead-list'),
    path('<int:pk>', views.LeadDetailView.as_view(), name='lead-details'),
    path('<int:pk>/update', views.LeadUpdateView.as_view(), name='lead-update'),
    path('<int:pk>/delete', views.LeadDeleteView.as_view(), name='lead-delete'),
    path('<int:pk>/assign-agent', views.AssignAgentView.as_view(), name='assign-agent'),
    path('<int:pk>/category', views.LeadCategoryUpdateView.as_view(), name='lead-category'),
    path('create', views.LeadCreateView.as_view(), name='create-lead'),
    path('categories', views.CategoryListView.as_view(), name='category-list'),
    path('category-create', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-details'),
    path('categories/<int:pk>/update', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete', views.CategoryDeleteView.as_view(), name='category-delete'),
]