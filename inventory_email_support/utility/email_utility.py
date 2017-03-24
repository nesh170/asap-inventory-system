from inventory_email_support.models import SubscribedManagers, SubjectTag
from post_office import mail



class EmailUtility:
    # TODO add the email templates to a fixutres and load it in the database
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
    def email(recipient, template, context, subject=None):
        # TODO add null check for email addresses (email not strictly required)
        subject_to_use = EmailUtility.get_subject(subject)
        context['subject'] = subject_to_use
        bcc_addresses = SubscribedManagers.objects.values_list('member__email', flat=True)[::1]
        # send_args = {'recipients': [recipient], 'sender': 'asap-inventory-system@kipcoonley.com', 'bcc': bcc_addresses,
        #              'template': template, 'context': context}
        # if priority is not None:
        #     send_args['priority'] = priority

        print("About to send email wee")
        #email_sent = mail.send(**send_args)
        mail.send(recipients=[recipient], sender='asap-inventory-system@kipcoonley.com',
                  priority='now', bcc=bcc_addresses, template=template, context=context)
        print("Email sent successfully")


