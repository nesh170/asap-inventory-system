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
        loan_reminder_date_today = LoanReminderSchedule.objects.filter(date=date.today(), executed=False)
        if loan_reminder_date_today.exists():
            for user in User.objects.filter(is_staff=False):
                # get loans with user from User table, cart status is filled (currently owned loans), returned timestamp
                # is null (not all quantities have been returned
                loaned_items = Loan.objects.filter(cart__owner=user, cart__status='fulfilled',
                                                   returned_timestamp__isnull=True).all()
                EmailUtility.email(recipient=user.email, template='loan_reminder',
                                   context={'name': user.username,
                                            'prepended_body': PrependedBody.objects.first().prepended_body,
                                            'loaned_items': loaned_items},
                                   subject="Reminder About Your Loaned Items")
                print("Reaching this line of cron job")
            first_loan_reminder_today = loan_reminder_date_today.first()
            first_loan_reminder_today.executed = True
            first_loan_reminder_today.save()
            print("date of today exists")
            print("hi there this is the end")
        else:
            pass
