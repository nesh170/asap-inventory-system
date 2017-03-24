from django_cron import CronJobBase, Schedule
from inventory_email_support.models import LoanReminderSchedule, PrependedBody
from inventory_email_support.utility.email_utility import EmailUtility
from inventory_requests.models import Loan
from datetime import date
from django.contrib.auth.models import User


class EmailCronJob(CronJobBase):
    RUN_AT_TIMES = ['1:55']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'inventoryProject.email_cron_job'    # a unique code

    def do(self):
        print("Running cron job YAY")
        if LoanReminderSchedule.objects.filter(date=date.today()).exists():
            for user in User.objects.filter(is_staff=False):
                # get loans with user from User table, cart status is filled (currently owned loans), returned timestamp
                # is null (not all quantities have been returned
                loaned_items = Loan.objects.filter(cart__owner=user, cart__status='fulfilled',
                                                   returned_timestamp__isnull=True).all()
                email_sent = EmailUtility.email(recipient=user.email, template='loan_reminder',
                                   context={'name': user.username,
                                            'prepended_body': PrependedBody.objects.first().prepended_body,
                                            'loaned_items': loaned_items},
                                   subject="Reminder About Your Loaned Items")
                print("Reaching this line of cron job")
                # TODO having trouble testing if this line works
                print(email_sent)
                if email_sent.status == 0:
                    print("Reaching this if statement")
                    LoanReminderSchedule.objects.get(date=date.today()).executed = True
        else:
            pass
