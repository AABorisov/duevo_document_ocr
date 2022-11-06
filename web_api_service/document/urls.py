from django.urls import path, include
from .views import *

urlpatterns = [
    path('dashboard/', login_required(DashboardView.as_view()), name='dashboard_url'),
    path('upload/', login_required(FileUploadView.as_view()), name='file_upload_url'),
    path('detail/<int:document_id>/<int:page_id>', login_required(DetailDocumentView.as_view()), name='document_detail_url'),
    path('page/<int:page_id>', login_required(PageDetailView.as_view()), name='page_detail_url'),
    path('document_json/', document_json_data, name='document_json_url'),
    path('generate_csv/', generate_csv_view, name='generate_csv_url'),
    path('generate_xml/', generate_xml_view, name='generate_xml_url'),
    path('nlp_json/', nlp_json_data, name='nlp_json_url'),
    path('stacked_chart_json/', stacked_chart_json, name='stacked_chart_json_url'),
    path('donut_chart_json/', donut_chart_json, name='donut_chart_json_url'),
    path('file_download/<int:file_id>', file_download, name='file_download_url'),
    path('convert_nlp/', convert_nlp_table_to_nlp_result, name='convert_nlp_table_to_nlp_result_url'),
    path('ajax_convert_nlp/', ajax_convert_nlp_table_to_nlp_result, name='ajax_convert_nlp_table_to_nlp_result_url'),
    # Ajax requests
    path('file_table_json/', ajax_file_table_json, name='ajax_file_table_json_url'),

    # Recalculate NLP
    path('google_nlp_recalculate/<int:document_id>', google_nlp_recalculate, name='google_nlp_recalculate_url'),
    path('tesseract_nlp_recalculate/<int:document_id>', tesseract_nlp_recalculate, name='tesseract_nlp_recalculate_url'),

    # Google layout
    path('add_ocr_record/', ajax_add_new_ocr_record, name='ajax_add_new_ocr_record_url'),
    path('edit_nlp_record/', ajax_edit_nlp_record, name='ajax_edit_nlp_record_url'),
    path('add_nlp_record/', ajax_add_nlp_record, name='ajax_add_nlp_record_url'),
    path('ocr_edit/', ajax_edit_ocr_table, name='ajax_edit_ocr_table_url'),
    path('ocr_remove/', ajax_remove_ocr_table, name='ajax_remove_ocr_table_url'),
    # Tesseract layout
    path('add_ocr_tesseract_record/', ajax_add_new_ocr_tesseract_record, name='ajax_add_new_ocr_tesseract_record_url'),
    path('edit_nlp_tesseract_record/', ajax_edit_nlp_tesseract_record, name='ajax_edit_nlp_tesseract_record_url'),
    path('add_nlp_tesseract_record/', ajax_add_nlp_tesseract_record, name='ajax_add_nlp_tesseract_record_url'),
    path('ocr_tesseract_edit/', ajax_edit_ocr_tesseract_table, name='ajax_edit_ocr_tesseract_table_url'),
    path('ocr_tesseract_remove/', ajax_remove_ocr_tesseract_table, name='ajax_remove_ocr_tesseract_table_url'),
    # Search
    path('global_search/', ajax_global_search, name='ajax_global_search_url'),

]
