import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill

from account.models import User
from document_processing import constants


def get_upload_path_pages(instance, filename):
    """Динамический путь для загрузки страниц из документа (JPEG)"""
    path = os.path.join("pages", str(instance.document.id), filename)
    return path

# def get_upload_path(instance, filename):
#     return '{0}/{1}'.format('pages/' + str(instance.document.id), filename)


class Status(models.Model):
    title = models.CharField(verbose_name=_('Status name'), max_length=255, null=True, unique=True)
    description = models.TextField(verbose_name=_('Description'), max_length=1000, null=True, blank=True)
    color = models.CharField(verbose_name=_('Color'), max_length=10, null=True, blank=True)
    is_detail = models.BooleanField(verbose_name=_('Is detail'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return str(self.title)


class Category(models.Model):
    title = models.CharField(verbose_name=_('Category name'), max_length=255, null=True)
    color = models.CharField(verbose_name=_('Color'), max_length=10, null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), max_length=2000, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return str(self.title)


class File(models.Model):
    """Таблица файлов - в одном файле может быть много отсканированных документов"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    original_name = models.CharField(verbose_name=_('Original name'), max_length=255, null=True, unique=True)
    description = models.TextField(verbose_name=_('Description'), max_length=2000, null=True, blank=True, db_index=True)
    file_path = models.FileField(verbose_name=_('File path'), upload_to='files/%Y/%m/%d/', null=True, blank=True)
    mime_type = models.CharField(verbose_name=_('Mime type'), max_length=50, null=True)
    is_processed = models.BooleanField(verbose_name=_('Is processed'), default=False)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return str(self.original_name)


class Document(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    description = models.TextField(verbose_name=_('Description'), max_length=2000, null=True, blank=True)
    is_processed = models.BooleanField(verbose_name=_('Is processed'), default=False)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return f'{self.file.original_name}'


class Page(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    original_name = models.CharField(verbose_name=_('Original name'), max_length=255, null=True, blank=True)
    page_number = models.IntegerField(verbose_name=_('Page number'), null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), max_length=2000, null=True, blank=True)
    page_image = models.ImageField(upload_to=get_upload_path_pages, null=True)
    page_thumbnail = ImageSpecField(source='page_image',
                                      processors=[ResizeToFill(500, 500)],
                                      format='JPEG',
                                      options={'quality': 60})

    # From Adygzhy
    page_id = models.IntegerField(verbose_name=_('Page ID'), null=True, blank=True)
    doc_id = models.IntegerField(verbose_name=_('Doc ID'), null=True, blank=True)
    page_link = models.TextField(verbose_name=_('Page link'), max_length=1000, null=True, blank=True)
    is_sent_to_server = models.BooleanField(verbose_name=_('Is sent'), default=False)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    dictionary = models.TextField(verbose_name=_('Page dictionary'), max_length=30000, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return f'{self.original_name}'


'''
class OcrResults(models.Model):
    doc_id = models.ForeignKey(Document, on_delete=models.DO_NOTHING, null=True)
    page_id = models.ForeignKey(Page, on_delete=models.DO_NOTHING, null=True)
    # page_id = models.BigIntegerField()
    ocr_text = models.TextField(blank=True, null=True)
    upper_left_y = models.IntegerField()
    upper_left_x = models.IntegerField()
    upper_right_y = models.IntegerField()
    upper_right_x = models.IntegerField()
    lower_right_y = models.IntegerField()
    lower_right_x = models.IntegerField()
    lower_left_y = models.IntegerField()
    lower_left_x = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ocr_results'

    def __str__(self):
        return f'DocID: {self.doc_id}; PageID: {self.page_id}; OcrText: {self.ocr_text}'
'''


class DocumentType(models.Model):
    doc_type_name = models.CharField(verbose_name=_('Document type'), max_length=255, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    class Meta:
        db_table = 'document_document_type'

    def __str__(self):
        return f'Doc type name: {self.doc_type_name}'


class AttributeLink(models.Model):
    """Таблица с общими именами полей для разных типов документов
    (например 'Кадастровый номер' может быть у 1го и 2го типа)
    """
    attribute_link_name = models.CharField(verbose_name=_('Attribute link name'), max_length=255, null=True, unique=True)
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    class Meta:
        db_table = 'document_attribute_link'

    def __str__(self):
        return f'Attribute link name: {self.attribute_link_name}'


class AttributeCategory(models.Model):
    category_name = models.CharField(verbose_name=_('Category name'), max_length=255, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    class Meta:
        db_table = 'document_attribute_category'

    def __str__(self):
        return f'Attribute Category: {self.category_name}'


class Attribute(models.Model):
    attribute_category = models.ForeignKey(AttributeCategory, on_delete=models.SET_NULL, blank=True, null=True)
    attribute_link = models.ForeignKey(AttributeLink, on_delete=models.SET_NULL, blank=True, null=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, null=True)
    attribute_name = models.CharField(verbose_name=_('Attribute name'), max_length=255, null=True, blank=True)
    is_required = models.BooleanField(verbose_name=_('Is required'), default=False)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return f'Тип документа: {self.document_type.id}; Имя атрибута: {self.attribute_name}'


class Ocr(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    ocr_text = models.TextField(verbose_name=_('OCR text'), max_length=1000, blank=True, null=True)
    user_text = models.TextField(verbose_name=_('OCR text'), max_length=1000, blank=True, null=True)
    upper_left_y = models.IntegerField(blank=True, null=True)   # y0 Andrei
    upper_left_x = models.IntegerField(blank=True, null=True)   # x0 Andrei
    upper_right_y = models.IntegerField(blank=True, null=True)
    upper_right_x = models.IntegerField(blank=True, null=True)
    lower_right_y = models.IntegerField(blank=True, null=True)  # y1 Andrei
    lower_right_x = models.IntegerField(blank=True, null=True)  # x1 Andrei
    lower_left_y = models.IntegerField(blank=True, null=True)
    lower_left_x = models.IntegerField(blank=True, null=True)
    status = models.SmallIntegerField(verbose_name=_('Status'), blank=True, null=True, default=2)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return f'DocID: {self.document.id}; PageID: {self.page.id}; OcrText: {self.ocr_text}'


class OcrTesseract(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    ocr_text = models.TextField(verbose_name=_('OCR text'), max_length=1000, blank=True, null=True)
    user_text = models.TextField(verbose_name=_('OCR text'), max_length=1000, blank=True, null=True)
    upper_left_y = models.IntegerField(blank=True, null=True)   # y0 Andrei
    upper_left_x = models.IntegerField(blank=True, null=True)   # x0 Andrei
    upper_right_y = models.IntegerField(blank=True, null=True)
    upper_right_x = models.IntegerField(blank=True, null=True)
    lower_right_y = models.IntegerField(blank=True, null=True)  # y1 Andrei
    lower_right_x = models.IntegerField(blank=True, null=True)  # x1 Andrei
    lower_left_y = models.IntegerField(blank=True, null=True)
    lower_left_x = models.IntegerField(blank=True, null=True)
    status = models.SmallIntegerField(verbose_name=_('Status'), blank=True, null=True, default=2)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    class Meta:
        db_table = 'document_ocr_tesseract'

    def __str__(self):
        return f'PageID: {self.page.id}; OcrText: {self.ocr_text}'


class Classification(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, null=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'DocID: {self.document.id}; PageID: {self.document_type.doc_type_name}'


class TesseractClassifier(models.Model):
    """Классификатор типов документов по собственному OCR"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'document_tesseract_classifier'

    def __str__(self):
        return f'DocID: {self.document.id}; PageID: {self.document_type.doc_type_name}'


class Nlp(models.Model):
    """
    status = 0 - not recognized word ids or text
    status = 1 - recognized word ids
    status = 2 - recognized only text (for ocr_text)
    status = 3 - operator add attribute with word ids
    status = 4 - new attribute
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, null=True)
    position = models.IntegerField(verbose_name=_('Position'), null=True, default=None)
    ocr_word_ids = models.JSONField(verbose_name=_('OCR word IDs'), null=True, default=None, blank=True)
    status = models.SmallIntegerField(verbose_name=_("Status"), choices=constants.STATUS_RECOGNITION_CHOICES, default=0)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    ocr_text = models.TextField(verbose_name=_("Ocr text"), max_length=2000, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return f'NlpID: {self.id}; Document: {self.document.id}; Attribute: {self.attribute.attribute_name} '


class NlpTesseract(models.Model):
    """
    status = 0 - not recognized word ids or text
    status = 1 - recognized word ids
    status = 2 - recognized only text (for ocr_text)
    status = 3 - operator add attribute with word ids
    status = 4 - new attribute
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, null=True)
    position = models.IntegerField(verbose_name=_('Position'), null=True, default=None)
    ocr_word_ids = models.JSONField(verbose_name=_('OCR word IDs'), null=True, default=None, blank=True)
    status = models.SmallIntegerField(verbose_name=_("Status"), choices=constants.STATUS_RECOGNITION_CHOICES, default=0)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    ocr_text = models.TextField(verbose_name=_("Ocr text"), max_length=2000, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    class Meta:
        db_table = 'document_nlp_tesseract'

    def __str__(self):
        return f'NlpID: {self.id}; Document: {self.document.id}; Attribute: {self.attribute.attribute_name} '


class NlpResult(models.Model):
    """Таблица для синхронизации основных полей из nlp"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    document_number = models.CharField(verbose_name=_('Document number'), max_length=255, null=True, blank=True, db_index=True)
    document_type = models.CharField(verbose_name=_('Document type'), max_length=255, null=True, blank=True, db_index=True)
    document_date = models.DateField(verbose_name=_('Document date'), null=True, blank=True, db_index=True)
    issuing_authority = models.TextField(verbose_name=_('Issuing authority'), max_length=4000, null=True, blank=True)
    cadastral_number = models.CharField(verbose_name=_('Сadastral number'), max_length=255, null=True, blank=True, db_index=True)
    administrative_district = models.CharField(verbose_name=_('Administrative district'), max_length=255, null=True, blank=True, db_index=True)
    district = models.CharField(verbose_name=_('District'), max_length=255, null=True, blank=True, db_index=True)
    address = models.TextField(verbose_name=_('Issuing authority'), max_length=4000, null=True, blank=True)
    object_name = models.TextField(verbose_name=_('Object name'), max_length=4000, null=True, blank=True)
    customer = models.TextField(verbose_name=_('Customer'), max_length=4000, null=True, blank=True)
    builder = models.TextField(verbose_name=_('Builder'), max_length=4000, null=True, blank=True)
    project_organization = models.CharField(verbose_name=_('Project organization'), max_length=255, null=True, blank=True, db_index=True)
    project_author_manager = models.CharField(verbose_name=_('Project author manager'), max_length=255, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    class Meta:
        db_table = 'document_nlp_result'

    def __str__(self):
        return f'NlpResultID: {self.id}'

class NlpOcrElement(models.Model):
    nlp = models.ForeignKey(Nlp, on_delete=models.CASCADE, null=True)
    ocr = models.ForeignKey(Attribute, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField(verbose_name=_('Position'), null=True, default=None)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    class Meta:
        db_table = 'document_nlp_ocr'

    def __str__(self):
        return f' Ocr: {self.ocr.attribute_name} '


class Schema(models.Model):
    """Show chart or plan coordinates for specific page"""
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    link = models.TextField(verbose_name=_('Link'), blank=True, null=True)
    orientation = models.IntegerField(verbose_name=_('Orientation'), blank=True, null=True)
    upper_left_y = models.IntegerField(blank=True, null=True)
    upper_left_x = models.IntegerField(blank=True, null=True)
    upper_right_y = models.IntegerField(blank=True, null=True)
    upper_right_x = models.IntegerField(blank=True, null=True)
    lower_right_y = models.IntegerField(blank=True, null=True)
    lower_right_x = models.IntegerField(blank=True, null=True)
    lower_left_y = models.IntegerField(blank=True, null=True)
    lower_left_x = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'Document: {self.page.document.id}; Ocr: {self.link} '

#
# Adygzhy models from PostgreSQL
#


class DocClasses(models.Model):
    class_name = models.CharField(max_length=2048)

    class Meta:
        managed = False
        db_table = 'doc_classes'

    def __str__(self):
        return f'Classification Name: {self.class_name}'


class DocClassificationResults(models.Model):
    doc_id = models.IntegerField(blank=True, null=True)
    class_field = models.ForeignKey(DocClasses, on_delete=models.DO_NOTHING, db_column='class_id', blank=True, null=True)  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'doc_classification_results'

    def __str__(self):
        return f'DocID: {self.doc_id}; Class: {self.class_field}'


class OcrResults(models.Model):
    doc_id = models.IntegerField(blank=True, null=True)
    page_id = models.IntegerField(blank=True, null=True)
    ocr_text = models.TextField(blank=True, null=True)
    upper_left_y = models.IntegerField(blank=True, null=True)
    upper_left_x = models.IntegerField(blank=True, null=True)
    upper_right_y = models.IntegerField(blank=True, null=True)
    upper_right_x = models.IntegerField(blank=True, null=True)
    lower_right_y = models.IntegerField(blank=True, null=True)
    lower_right_x = models.IntegerField(blank=True, null=True)
    lower_left_y = models.IntegerField(blank=True, null=True)
    lower_left_x = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    user_text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ocr_results'

    def __str__(self):
        return f'DocID: {self.doc_id}; PageID: {self.page_id}; OcrText: {self.ocr_text}'


class BtiDocuments(models.Model):
    doc_id = models.IntegerField(blank=True, null=True)
    class_field = models.ForeignKey(DocClasses, models.DO_NOTHING, db_column='class_id', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    number = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    issuing_authority = models.TextField(blank=True, null=True)
    documentation_source = models.TextField(blank=True, null=True)
    date_of_completion = models.TextField(blank=True, null=True)
    object_name = models.TextField(blank=True, null=True)
    inventory_number = models.TextField(blank=True, null=True)
    main_characteristic_value = models.TextField(blank=True, null=True)
    year_built = models.TextField(blank=True, null=True)
    commissioning_year = models.TextField(blank=True, null=True)
    cadastral_number_zu = models.TextField(blank=True, null=True)
    cadastral_number_oks = models.TextField(blank=True, null=True)
    building_plan_stamp_recognition = models.TextField(blank=True, null=True)
    building_plan_stamp_date_of_completion = models.TextField(blank=True, null=True)
    building_plan_stamp_date_of_modification = models.TextField(blank=True, null=True)
    building_plan_stamp_owner_name = models.TextField(blank=True, null=True)
    object_composition_object = models.TextField(blank=True, null=True)
    object_composition_name = models.TextField(blank=True, null=True)
    object_composition_year = models.TextField(blank=True, null=True)
    object_composition_area = models.TextField(blank=True, null=True)
    land_explication_explication = models.TextField(blank=True, null=True)
    land_explication_area = models.TextField(blank=True, null=True)
    land_explication_address = models.TextField(blank=True, null=True)
    land_explication_purpose = models.TextField(blank=True, null=True)
    land_explication_marks = models.TextField(blank=True, null=True)
    land_explication_date = models.TextField(blank=True, null=True)
    land_explication_date_of_modification = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bti_documents'

    def __str__(self):
        return f'DocID: {self.doc_id}; Class: {self.class_field.class_name}; number: {self.number}'


class SvidAgrDocuments(models.Model):
    doc_id = models.IntegerField(blank=True, null=True)
    class_field = models.ForeignKey(DocClasses, models.DO_NOTHING, db_column='class_id', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    number = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    issuing_authority = models.TextField(blank=True, null=True)
    administrative_district = models.TextField(blank=True, null=True)
    district = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    object_name = models.TextField(blank=True, null=True)
    functional_purpose_of_object = models.TextField(blank=True, null=True)
    customer = models.TextField(blank=True, null=True)
    builder = models.TextField(blank=True, null=True)
    project_organization = models.TextField(blank=True, null=True)
    project_author_manager = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'svid_agr_documents'

    def __str__(self):
        return f'DocID: {self.doc_id}; Class: {self.class_field.class_name}; number: {self.number}'


class DocSchemas(models.Model):
    doc_id = models.IntegerField(blank=True, null=True)
    page_id = models.IntegerField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    orientation = models.IntegerField()
    upper_left_y = models.IntegerField()
    upper_left_x = models.IntegerField()
    upper_right_y = models.IntegerField()
    upper_right_x = models.IntegerField()
    lower_right_y = models.IntegerField()
    lower_right_x = models.IntegerField()
    lower_left_y = models.IntegerField()
    lower_left_x = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'doc_schemas'


class NlpOcr(models.Model):
    attribute = models.TextField(blank=True, null=True)
    nlp = models.ForeignKey(SvidAgrDocuments, models.DO_NOTHING)
    ocr = models.ForeignKey(OcrResults, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nlp_ocr'

    def __str__(self):
        return f'Attr: {self.attribute}; NLP NUM: {self.nlp.number}; OCR WORD: {self.ocr.ocr_text}'
