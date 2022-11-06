from django.utils.translation import gettext_lazy as _


GENDER_CHOICES = (
    (0, _('Male')),
    (1, _('Female')),
    (2, _('Other')),
)

STATUS_RECOGNITION_CHOICES = (
    (0, _('Not recognized')),
    (1, _('Recognized')),
    (2, _('Operator recognized')),
    (3, _('Operator add attribute with word ids')),
    (4, _('New attribute')),
)

EMAIL_NOTIFY_CHOICES = (
    (0, _('Disable')),
    (1, _('Enable')),
)

# PAGE_STATUS_CHOICES = (
#     (0, _('Disable')),
#     (1, _('Enable')),
# )

ROOM_TYPE_CHOICES = (
    (0, _('Public')),
    (1, _('Private')),
    (2, _('Hidden')),
)

MESSAGE_STATUS_CHOICES = (
    (0, _('Deleted')),
    (1, _('Active')),
    (2, _('Hidden')),
)

INVITE_REASON_CHOICES = (
    (0, _('Create room')),
    (1, _('Buy ticket')),
    (2, _('Owner add')),
    (3, _('Free access')),
)

# NAVBAR names
NAVBAR_MAIN = 'navbar_main'
NAVBAR_DASHBOARD = 'navbar_dashboard'
NAVBAR_PROFILE = 'navbar_profile'
NAVBAR_DOCUMENT_UPLOAD = 'navbar_document_upload'
NAVBAR_DOCUMENT_DETAIL = 'navbar_document_detail'
NAVBAR_PAGE_DETAIL = 'navbar_page_detail'

# Group
GROUP_INSTRUCTOR = "Instructor"
