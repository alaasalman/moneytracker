import logging
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from walletweb import models

logger = logging.getLogger('moneytracker')


class Command(BaseCommand):
    help = 'Add tags to users'

    def handle(self, *args, **options):
        current_dt = datetime.datetime.now()

        default_tags = ['Shopping', 'Transportation',
                        'Utilities', 'Salary',
                        'Misc', 'Recurring']
        all_users = models.WalletyUser.objects.all()

        for user in all_users:
            for default_tag in default_tags:
                if not models.Tag.objects.filter(user=user, name=default_tag).exists():
                    # default tag does not exist, create it
                    tag = models.Tag()
                    tag.user = user
                    tag.name = default_tag
                    tag.slug = slugify(tag.name)
                    tag.save()

        self.stdout.write(self.style.SUCCESS('Ran addtag command {0}'.format(current_dt)))
