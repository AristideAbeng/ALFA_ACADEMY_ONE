from django.urls import path
from .views import GetAffiliateByUserID , GetAffiliateStatisticsByUserID

urlpatterns = [
    path('affiliate/<int:user_id>/', GetAffiliateByUserID.as_view(), name='get-affiliate'),
    path('affiliates/statistics/<int:user_id>/', GetAffiliateStatisticsByUserID.as_view(), name='affiliate-statistics'),
]
