from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
# from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from account.models import User
from document.models import Document, SvidAgrDocuments, DocClasses
from document.api.serializers import DocumentSerializer, SvidAgrDocumentsSerializer, DocClassesSerializer
from django.utils.translation import gettext_lazy as _


class ApiNlpListView(ListAPIView):
    queryset = SvidAgrDocuments.objects.all().using('ocr')
    serializer_class = SvidAgrDocumentsSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('class_field__class_name', 'number', 'date', 'issuing_authority', 'customer', 'builder', 'project_organization', 'project_author_manager')
    # search_fields = ['number', ]


class ApiDocTypeListView(ListAPIView):
    queryset = DocClasses.objects.all().using('ocr')
    serializer_class = DocClassesSerializer


@api_view(['GET', ])
def api_detail_document_view(request, document_id):
    try:
        document = Document.objects.get(id=document_id, is_active=True)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentSerializer(document)
        print(serializer.data)
        return Response(serializer.data)


@api_view(['GET', ])
def api_npl_detail_view(request, nlp_id):
    try:
        nlp = SvidAgrDocuments.objects.using('ocr').get(id=nlp_id)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SvidAgrDocumentsSerializer(nlp)
        print(serializer.data)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_document_view(request, document_id):
    try:
        document = Document.objects.get(id=document_id, is_active=True)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = DocumentSerializer(document, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'update successful'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['DELETE', ])
# def api_delete_document_view(request, document_id):
#     try:
#         document = Document.objects.get(id=document_id, is_active=True)
#     except Document.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'DELETE':
#         operation = document.delete()
#         data = {}
#         if operation:
#             data['success'] = 'delete successful'
#         else:
#             data['dailure'] = 'delete failed'
#         return Response(data=data)


@api_view(['POST', ])
def api_create_document_view(request):

    user = User.objects.get(id=1)

    document = Document(
        user=user,
        category_id=1,
    )

    if request.method == 'POST':
        serializer = DocumentSerializer(document, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


