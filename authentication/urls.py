from django.urls import path
from . import views



urlpatterns = [
 path('signup/',views.UserCreateView.as_view(),name='signup view'),
  path('<user_email>/', views.UserGetDetailView.as_view(), name='get_detail_user'),
]