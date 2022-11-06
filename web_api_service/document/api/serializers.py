from rest_framework import serializers
from document.models import *


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'user', 'category', 'status', 'original_name', 'description', 'document_path', 'mime_type', 'is_processed', 'is_active']


class SvidAgrDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SvidAgrDocuments
        fields = ['id', 'doc_id', 'class_field', 'number', 'date', 'issuing_authority', 'administrative_district',
                  'district', 'address', 'object_name', 'functional_purpose_of_object', 'customer', 'builder',
                  'project_organization', 'project_author_manager']


class DocClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocClasses
        fields = ['id', 'class_name']
