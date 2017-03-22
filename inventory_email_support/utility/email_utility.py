from inventory_email_support.models import SubscribedManagers, SubjectTag
from post_office import mail
from post_office.models import EmailTemplate

# class CreateEmailTemplate:
#     @staticmethod
#     def create():
#         EmailTemplate.objects.create(
#             name='request_created',
#             subject='{{ subject }}',
#             html_content='<p> Hi {{ name }}, </p> <p> Your request was successfully submitted! A staff member will take a '
#                  'look at it as soon as possible. </p> <p> Best Regards, <br /> ECE Inventory System Staff </p>'
#         )


class EmailUtility:
    # TODO add the email templates to a fixutres and load it in the database
    # TODO check if referencing things by pk=1 is okay
    #CreateEmailTemplate.create()
    @staticmethod
    def get_subject(subject=None):
        if SubjectTag.objects.count() == 0:
            if subject is not None:
                subject_to_return = subject
            else:
                subject_to_return = ''
        # subject tag exists
        else:
            subject_tag = SubjectTag.objects.get(pk=1)
            print("About to print subject tag: " + subject_tag.subject_tag)
            if subject is not None:
                subject_tag_string = "[{subject_tag}] {subject}".format
                subject_to_return = subject_tag_string(subject_tag=subject_tag.subject_tag, subject=subject)
            else:
                subject_tag_string = "[{subject_tag}]".format
                subject_to_return = subject_tag_string(subject_tag=subject_tag.subject_tag)
        return subject_to_return

    @staticmethod
    def email(template, context, subject=None):
        # TODO add null check for email addresses (email not strictly required)
        subject_to_use = EmailUtility.get_subject(subject)
        context['subject'] = subject_to_use
        bcc_addresses = SubscribedManagers.objects.values_list('member__email', flat=True)[::1]
        print("About to send email wee")
        mail.send(recipients=['ak308@duke.edu'], sender='asap-inventory-system@kipcoonley.com',
                  priority='now', bcc=bcc_addresses, template=template, context=context)
        print("Email sent successfully")


