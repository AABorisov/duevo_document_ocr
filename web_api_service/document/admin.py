from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "title", "is_active")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("id", "document_id", "original_name", "page_number", "status_id", "is_sent_to_server")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "status", "is_processed", "is_active")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "is_detail")


@admin.register(AttributeLink)
class AttributeLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "attribute_link_name", "is_active")


@admin.register(NlpResult)
class NlpResultAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "document_number", "document_date", "issuing_authority", "is_active")


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "document_type", "attribute_name", "is_required", "is_active")


@admin.register(Nlp)
class NlpAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "attribute", "status", "is_active")


@admin.register(NlpTesseract)
class NlpTesseractAdmin(admin.ModelAdmin):
    list_display = ("id", "document_id", "attribute_id", "status", "is_active")


@admin.register(Ocr)
class OcrAdmin(admin.ModelAdmin):
    list_display = ("id", "ocr_text", "user_text", "status", "is_active")


@admin.register(OcrTesseract)
class OcrTesseractAdmin(admin.ModelAdmin):
    list_display = ("id", "ocr_text", "user_text", "status", "is_active")


@admin.register(TesseractClassifier)
class TesseractClassifierAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "document_type")


admin.site.register(AttributeCategory)
admin.site.register(Classification)
admin.site.register(DocumentType)
admin.site.register(NlpOcrElement)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "created_at")
