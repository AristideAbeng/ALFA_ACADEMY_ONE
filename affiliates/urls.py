from django.urls import path
from .views import GetAffiliateByUserID

urlpatterns = [
    path('affiliate/<int:user_id>/', GetAffiliateByUserID.as_view(), name='get-affiliate'),
]
