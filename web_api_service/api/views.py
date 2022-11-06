from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from account.models import User
from document.models import Document
from api.serializers import DocumentSerializer


@api_view(['GET', ])
def api_detail_document_view(request, document_id):
    try:
        document = Document.objects.get(id=document_id, is_active=True)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentSerializer(document)
        return Response(serializer.data)