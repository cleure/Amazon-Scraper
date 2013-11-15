from notifications import *

import smtplib
from email.mime.text import MIMEText

class SMTP_Notification(Notification):
    def __init__(self, host, from_addr, to_addr, **kwargs):
        defaults = dict(
            local_hostname=None,
            keyfile=None,
            certfile=None,
            user=None,
            password=None,
            ssl=False,
            port=25,
            email_subject='Amazon Scraper Notification'
        )

        self.host = host
        self.from_addr = from_addr
        self.to_addr = to_addr
        
        for k, v in kwargs.items():
            if k in defaults:
                defaults[k] = v

        if defaults['ssl'] == True and 'port' not in kwargs:
            defaults['port'] = 465

        for k, v in defaults.items():
            self.__dict__[k] = v

    def invoke( self,
                product,
                product_group,
                product_price,
                invoked_rule=None):

        if self.ssl == True:
            kwargs = {}
            for k in ['host', 'port', 'local_hostname', 'keyfile', 'certfile']:
                if self.__dict__[k] is not None:
                    kwargs[k] = self.__dict__[k]
        
            mail = smtplib.SMTP_SSL(**kwargs)
        else:
            kwargs = {}
            for k in ['host', 'port', 'local_hostname']:
                if self.__dict__[k] is not None:
                    kwargs[k] = self.__dict__[k]

            mail = smtplib.SMTP(**kwargs)

        if self.user is not None and self.password is not None:
            mail.login(self.user, self.password)

        if (not isinstance(self.to_addr, list) and
            not isinstance(self.to_addr, tuple)):
            self.to_addr = [self.to_addr]

        msg = MIMEText('This is a test')
        msg['Subject'] = self.email_subject
        msg['From'] = self.from_addr
        msg['To'] = self.to_addr[0]

        mail.sendmail(self.from_addr, self.to_addr, msg.as_string())

API_NOTIFICATION_CLASS = SMTP_Notification
