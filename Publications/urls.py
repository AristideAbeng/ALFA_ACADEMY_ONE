from django.urls import path
from .views import GetAllPublications, PublicationDetail

urlpatterns = [
    path('publications/', GetAllPublications.as_view(), name='get_all_publications'),
    path('publications/<int:publication_id>/', PublicationDetail.as_view(), name='publication_detail'),
]
