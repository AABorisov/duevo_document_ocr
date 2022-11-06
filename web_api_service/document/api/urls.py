from django.urls import path

from document.api.views import api_detail_document_view, api_update_document_view, \
     api_create_document_view, ApiNlpListView, ApiDocTypeListView, api_npl_detail_view

app_name = 'document'

urlpatterns = [
    # path('create/<int:documnet_id>', api_detail_document_view, name='create'),
    # path('edit/<int:documnet_id>', api_detail_document_view, name='edit'),
    path('document/detail/<int:document_id>', api_detail_document_view, name='detail'),
    path('document/update/<int:document_id>', api_update_document_view, name='update'),
    # path('document/delete/<int:document_id>', api_delete_document_view, name='delete'),
    path('document/create/', api_create_document_view, name='create'),
    path('document/nlp/all/', ApiNlpListView.as_view(), name='nlp_all'),
    path('document/nlp/detail/<int:nlp_id>', api_npl_detail_view, name='nlp_detail'),
    path('document/doc_type/all/', ApiDocTypeListView.as_view(), name='doc_type'),

]
