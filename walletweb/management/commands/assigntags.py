import logging
import datetime

from django.core.management.base import BaseCommand, CommandError
from walletweb import models

logger = logging.getLogger('moneytracker')


class Command(BaseCommand):
    help = 'Auto assigns tags to tag-less transactions'

    def handle(self, *args, **options):
        current_dt = datetime.datetime.now()

        tagless_transactions = models.Transaction.objects.filter(tags__isnull=True)

        logger.info('Trying to autoassign tags to {0}'.format(tagless_transactions.count()))

        for ttrans in tagless_transactions:
            tagdifflist = []
            trans_description_list = ttrans.description.split()
            trans_description_list = list(map(lambda word: word.lower(), trans_description_list))

            user_tags = models.Tag.objects.filter(user=ttrans.user, words__isnull=False)

            for utag in user_tags:
                # fetch words associated to tag
                utag_words = list(map(lambda word: word.lower(), utag.words))

                # if description has any of those words
                diffset = set(utag_words) & set(trans_description_list)
                if diffset != set():
                    tagdifflist.append((len(diffset), utag.name))

            tagdifflist.sort(key=lambda item: item[0], reverse=True)

            if len(tagdifflist) > 0:
                # tags needs to be assigned to transaction
                tagnametoassign = tagdifflist[0][1]
                ttrans.tags.add(tagnametoassign)

                self.stdout.write(self.style.SUCCESS('Assign tag {0} to transaction {1}'.format(tagnametoassign, ttrans.id)))
                logger.info('Assign tag {0} to transaction {1}'.format(tagnametoassign, ttrans.id))

        self.stdout.write(self.style.SUCCESS('Ran autotag command {0}'.format(current_dt)))
