#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    script used to send the resume of events of day for professional
'''

import sys
import locale
from os import environ

reload(sys)
sys.setdefaultencoding("utf-8")
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

environ['DJANGO_SETTINGS_MODULE'] = 'gestorpsi.settings'
sys.path.append('..')

from datetime import date, timedelta
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context

from gestorpsi.schedule.models import Occurrence

# check if exist events of next day for all professionals
dt = date.today() + timedelta(1) # correct

# main code
week_days = (u'Segunda-feira', u'Terça-feira', u'Quarta-feira', u'Quinta-feira', u'Sexta-feira', u'Sábado', u'Domingo')
d = dt.day
m = dt.month
y = dt.year

# sent professional list
sent = []

# all occurrence of next day
for o in Occurrence.objects.filter(start_time__year=y, start_time__month=m, start_time__day=d): # correct
#for o in Occurrence.objects.filter(start_time__year=y, start_time__month=m, start_time__day=d, event__referral__organization__id='bcbfdb8e-1641-4478-9e7c-3e0f1befbede'): # test
    # for each professional
    for p in o.event.referral.professional.all():

        to = []
        oc_list = [] # occurrence list

        # professional whant to receive resume occurrences of next day by email?
        if p.person.notify.all() and p.person.notify.all()[0].resume_daily_event and p not in sent:
            sent.append(p) # to check professional, avoid duplicate

            for x in p.person.emails.all():
                to.append(u'%s' % x.email)

            # send email
            if to:
                title = u"GestorPsi - Resumo dos eventos para %s, %s.\n\n" % (week_days[date.today().weekday()], dt.strftime('%d %b %Y') )

                # render occurrence
                for x in Occurrence.objects.filter(start_time__year=y, start_time__month=m, start_time__day=d, event__referral__professional=p).order_by('start_time'):
                    oc_list.append(x)

                # render html email
                text = Context({'oc_list':oc_list, 'title':title})
                template = get_template("schedule/schedule_notify_careprofessional.html").render(text)
                # sendmail
                msg = EmailMessage()
                msg.content_subtype = 'html'
                msg.encoding = "utf-8"
                msg.subject = u"GestorPsi - Resumo diário dos eventos."
                msg.body = template
                msg.to = to
                msg.send()
