from datetime import date, datetime

from post_office import mail


class EmailUtility:
    @staticmethod
    def email():
        print("About to send email wee")
        mail.send(recipients='ankit.kayastha@duke.edu', sender='ankitkayastha@gmail.com', subject="hi", message="Hi there", priority='now')
        print("Email sent successfully")