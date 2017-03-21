from datetime import date, datetime

from post_office import mail


class EmailUtility:
    @staticmethod
    def email():
        print("About to send email wee")
        mail.send(recipients=['ak308@duke.edu'], sender='asap-inventory-system@kipcoonley.com', subject="hi", message="Hi there this is a message", priority='now')
        print("Email sent successfully")