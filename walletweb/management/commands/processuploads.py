import logging
import datetime
import csv

from django.core.management.base import BaseCommand, CommandError
from dateutil import parser as dateutilparser

from walletweb import models

logger = logging.getLogger('moneytracker')


class Command(BaseCommand):
    help = 'Process CSV export uploads'

    def handle(self, *args, **options):
        current_dt = datetime.datetime.now()

        logger.info(f"Processing uploads at {current_dt}")

        uploads = models.FileUpload.objects.filter(processed=False)

        for upload in uploads:
            user_currency = upload.user.userprofile.display_currency

            with open(upload.name) as datafile:
                if upload.uploadtype == models.FileUpload.UPLOAD_TRANSACTIONS_ING:
                    csv_dictreader = csv.DictReader(datafile)
                elif upload.uploadtype == models.FileUpload.UPLOAD_TRANSACTIONS_CBA:
                    # CBA export has no column names, so set them
                    csv_dictreader = csv.DictReader(datafile, ['Date', 'Amount', 'Description', 'Balance'])
                else:
                    # only support specific export files for now
                    continue

                for record in csv_dictreader:
                    record_date = dateutilparser.parse(record['Date'], dayfirst=True).date()
                    record_description = record['Description']
                    record_balance = record['Balance']

                    if upload.uploadtype == models.FileUpload.UPLOAD_TRANSACTIONS_CBA:
                        # CBA uses +ve/-ve for credit debit
                        record_amount = record['Amount']
                    elif upload.uploadtype == models.FileUpload.UPLOAD_TRANSACTIONS_ING:
                        record_amount = record['Credit'] or record['Debit']
                    else:
                        # only support specific export files for now
                        continue

                    new_trans = models.Transaction()
                    new_trans.date = record_date
                    new_trans.amount = record_amount
                    new_trans.description = record_description
                    new_trans.user = upload.user

                    if upload.account:
                        # account was specified on upload
                        new_trans.account = upload.account
                        new_trans.currency = upload.account.currency
                    else:
                        new_trans.currency = user_currency

                    new_trans_sig = models.Transaction.sign_transaction(new_trans, extra=record_balance)

                    if models.Transaction.objects.filter(user=upload.user, signature=new_trans_sig).exists():
                        new_trans.description += "[dup]"

                    new_trans.signature = new_trans_sig
                    # mark that this transaction is from a specific upload
                    new_trans.extra = {
                        'fromupload': upload.id
                    }

                    new_trans.save()

            # mark as processed
            upload.processed = True
            upload.save()
