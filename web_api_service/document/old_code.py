class DocumentUploadView(View):

    @staticmethod
    def get(request):
        categories = Category.objects.filter(is_active=True)
        page = Document.objects.last()
        print(page.id)
        context = {
            "categories": categories,
            "title": _("Document upload"),
            "navbar": constants.NAVBAR_DOCUMENT_UPLOAD,
        }
        return render(request, 'document/document_upload.html', context=context)

    @staticmethod
    def post(request):
        print(request.POST.get('category'))
        print(request.FILES.getlist('files'))

        # Creates 'documents' dir
        documents_path = os.path.join(settings.MEDIA_ROOT, 'documents')
        if not os.path.exists(documents_path):
            os.mkdir(documents_path)

        fs = FileSystemStorage()

        category_id = request.POST.get('category')
        description = request.POST.get('description')
        pages_path = os.path.join(settings.BASE_DIR, 'media', 'pages')
        page_short_path = 'pages/'
        duplicate_files = []

        for file in request.FILES.getlist('files'):
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(file.read())
            extension = mime_type.split('/').pop()
            print(extension)
            print(mime_type)
            original_name = file.name
            document_path = fs.save('documents/' + file.name, file)
            print(document_path)
            print('ORIGINAL_NAME: ' + original_name)
            # Upload photo to Processing server

            # Check in database if document exists
            document_exist = is_document_exists(original_name)

            if document_exist is False:

                document = Document.objects.create(
                    user_id=request.user.id,
                    category_id=category_id,
                    status_id=1,
                    original_name=original_name,
                    description=description,
                    document_path=document_path,
                    mime_type=mime_type,
                )
                document.save()
                print('ORIG NAME: ' + document.original_name)

                doc_id = str(document.id)

                file_path = os.path.join(settings.BASE_DIR, 'media', document_path)
                print('FILE PATH: ' + file_path)

                # Work with PDF
                pages = convert_from_path(file_path, 300)

                print(pages)
                cnt = 0
                for page in pages:
                    cnt += 1
                    last_page_id = str(get_last_page_id())
                    print('LAST PAGE ID: ' + last_page_id)
                    new_pagename = doc_id + '_' + last_page_id + '.jpeg'
                    jpeg_name = os.path.join(pages_path, new_pagename)
                    page.save(jpeg_name, 'JPEG')
                    print('NEW PAGE NAME: ' + new_pagename)
                    '''
                    url = 'http://89.223.95.49:8887/upload'
                    full_path = os.path.join(str(settings.BASE_DIR), 'media', str(document_path))

                    files = {'media': open(full_path, 'rb')}
                    response = requests.post(url, files=files)
                    json_string = response.text
                    print(json_string)
                    json_data = json.loads(json_string)
                    page_link = json_data[0]['Link']
                    task_id = json_data[0]['TaskId']
                    doc_id = json_data[0]['DocId']
                    '''
                    page_db = Page.objects.create(

                        document_id=document.id,
                        status_id=1,
                        original_name=new_pagename,
                        page_number=cnt,
                        page_image=page_short_path + new_pagename,

                        # page_link=page_link,
                        # task_id=task_id,
                        # doc_id=doc_id,

                    )
                    page_db.save()

            else:
                duplicate_files.append(original_name)

        print(duplicate_files)
        print(len(duplicate_files))

        if len(duplicate_files) != 0:
            for duplicate_file in duplicate_files:
                message_text = _(f'This file "{duplicate_file}" duplicated!')
                messages.warning(request, message_text)

        message_text = _('Documents uploaded successfully!')
        messages.success(request, message_text)

        return redirect('dashboard_url')
