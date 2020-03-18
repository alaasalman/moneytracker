import datetime
import logging

from django.core.management.base import BaseCommand, CommandError
from walletweb.models import RecurringTransaction, Transaction
from walletweb import models

logger = logging.getLogger('moneytracker')


class Command(BaseCommand):
    help = 'Checks and executes any recurring transactions'

    def handle(self, *args, **options):
        current_dt = datetime.date.today()
        manytimes = 0

        logger.info(f'Applying recurrent transactions at {current_dt}')

        for rtrans in RecurringTransaction.objects.all():

            # get recurrent user
            recurrent_user = rtrans.account.user

            # get user recurrent tag
            recurrent_tag = models.Tag.objects.filter(user=recurrent_user, name='Recurring').first()

            # get display currency
            trans_currency = recurrent_user.userprofile.display_currency

            # if he doesn't have a recurrent tag, create it
            if recurrent_tag is None:
                recurrent_tag = models.Tag.objects.create(user=recurrent_user, name='Recurring')

            rtransdate = rtrans.lastdone or rtrans.date
            datediff = current_dt - rtransdate  # timedelta since transaction lastdone or creation

            if rtrans.repeattype == RecurringTransaction.REPEAT_DAILY:
                manytimes = datediff.days / rtrans.repeatevery
            elif rtrans.repeattype == RecurringTransaction.REPEAT_WEEKLY:
                datediffweeks = datediff.days / 7
                manytimes = datediffweeks / rtrans.repeatevery
            elif rtrans.repeattype == RecurringTransaction.REPEAT_MONTHLY:
                datediffmonths = datediff.days / 30
                manytimes = datediffmonths / rtrans.repeatevery
            elif rtrans.repeattype == RecurringTransaction.REPEAT_YEARLY:
                datediffyears = datediff.days / 365
                manytimes = datediffyears / rtrans.repeatevery

            for i in range(int(manytimes)):
                trans = Transaction()
                trans.user = recurrent_user
                trans.account = rtrans.account
                trans.amount = rtrans.amount
                trans.description = rtrans.description

                if rtrans.repeattype == RecurringTransaction.REPEAT_DAILY:
                    transdate = rtransdate + datetime.timedelta(days=i)
                elif rtrans.repeattype == RecurringTransaction.REPEAT_WEEKLY:
                    transdate = rtransdate + datetime.timedelta(weeks=i)
                elif rtrans.repeattype == RecurringTransaction.REPEAT_MONTHLY:
                    transdate = rtransdate + datetime.timedelta(days=i * 30)
                elif rtrans.repeattype == RecurringTransaction.REPEAT_YEARLY:
                    transdate = rtransdate + datetime.timedelta(days=i * 365)

                trans.currency = trans_currency
                trans.date = transdate
                trans.save()

                # assign recurrent tag to all created transactions
                trans.tags.add(recurrent_tag.name)

                self.stdout.write(self.style.SUCCESS('Adding transaction {0}'.format(trans)))

                # on transaction, update recurring transaction record
                rtrans.lastdone = current_dt

            rtrans.save()

            self.stdout.write(
                self.style.SUCCESS('Successfully checked/applied recurring transaction {0}'.format(rtrans)))
