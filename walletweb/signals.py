from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from walletweb.models import WalletyUser, Tag, Currency, UserProfile


@receiver(post_save, sender=WalletyUser)
def after_user_saved(sender, **kwargs):
    user = kwargs['instance']
    user_created = kwargs['created']

    # if user created assign default currency to it via a new profile
    if user_created or not hasattr(user, 'userprofile'):
        default_currency = Currency.objects.first()
        profile = UserProfile(user=user, display_currency=default_currency)
        profile.save()

        user.userprofile = profile
        user.save()

    if not Tag.objects.filter(user=user).exists():
        # user has no tags, create some default ones
        for default_tag_name in ['Shopping', 'Transportation',
                                 'Utilities', 'Salary',
                                 'Misc', 'Recurring']:
            tag = Tag()
            tag.name = default_tag_name
            tag.slug = slugify(default_tag_name)
            tag.user = user
            tag.save()
