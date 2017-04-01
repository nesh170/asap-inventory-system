from inventory_email_support.models import SubscribedManagers, SubjectTag
from post_office import mail


class EmailUtility:
    @staticmethod
    def get_subject(subject=None):
        if not SubjectTag.objects.exists():
            subject_to_return = subject if subject else ''
        # subject tag exists
        else:
            subject_tag = SubjectTag.objects.first()
            if subject is not None:
                subject_tag_string = "[{subject_tag}] {subject}".format
                subject_to_return = subject_tag_string(subject_tag=subject_tag.subject_tag, subject=subject)
            else:
                subject_tag_string = "[{subject_tag}]".format
                subject_to_return = subject_tag_string(subject_tag=subject_tag.subject_tag)
        return subject_to_return

    @staticmethod
    def email(recipient, template, context, subject=None):
        subject_to_use = EmailUtility.get_subject(subject)
        context['subject'] = subject_to_use
        bcc_addresses = SubscribedManagers.objects.filter(member__email__isnull=False)\
            .values_list('member__email', flat=True)[::1]\
            if SubscribedManagers.objects.exists() else []
        bcc_addresses = [address for address in bcc_addresses if address]
        if recipient:
            recipient = recipient if type(recipient) == 'list' else [recipient]
            mail.send(recipients=recipient, sender='asap.inventory.system@gmail.com',
                      priority='now', bcc=bcc_addresses, template=template, context=context)
