from rest_framework import serializers
from document.models import *


class DocumentSerializer(serializers.Serializer):
    class Meta:
        model = Document
        fields = ['id', 'user', 'category', 'status', 'original_name', 'description', 'document_path', 'mime_type', 'is_processed', 'is_active']
