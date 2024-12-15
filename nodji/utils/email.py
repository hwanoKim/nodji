# -*- coding: utf-8 -*-
"""
메일 전송을 위한 모듈
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Email:

    def __init__(self, email='sin3514@naver.com', password='YVK4VZYULDY1', server='naver'):
        self.email = email
        self.password = password
        self.server = server
        self.recipient = []
        self._login()

    def _login(self):
        if self.server == 'naver':
            self.smtp = smtplib.SMTP('smtp.naver.com', 587)
            self.smtp.ehlo()
            self.smtp.starttls()
            self.smtp.login(self.email, self.password)

        self.msg = MIMEMultipart()
        self.msg['From'] = self.email

    def _set_subject(self, subject):
        self.msg['Subject'] = subject

    def _add_msg(self, msg):
        mMsg = MIMEText(msg)
        self.msg.attach(mMsg)

    def send(self, subject='NODJI에서 메일을 보내드립니다', msg='테스트 메세지 입니다', recipient=None):
        self._set_subject(subject)
        self._add_msg(msg)
        if recipient is None:
            recipient = self.email
        self.msg['To'] = recipient
        self.smtp.sendmail(self.email, recipient, self.msg.as_string())
