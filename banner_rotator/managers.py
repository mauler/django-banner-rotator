from random import random, sample
from decimal import Decimal

from django.db import models


def pick(bias_list):
    """
    Takes a list similar to [(item1, item1_weight), (item2, item2_weight),]
        and item(n)_weight as the probability when calculating an item to choose
    """

    # All weights should add up to 1
    #   an items weight is equivalent to it's probability of being picked
    assert sum(i[1] for i in bias_list) == 1

    # Django ORM returns floats as Decimals,
    #   so we'll convert floats to decimals here to co-operate
    number = Decimal("%.18f" % random())
    current = Decimal(0)

    # With help from
    #   @link http://fr.w3support.net/index.php?db=so&id=479236
    for choice, bias in bias_list:
        current += Decimal("%.15g" % bias)
        if number <= current:
            return choice


class BiasedManager(models.Manager):
    """
    Select a *random* banner, from a biased queryset
        - (banners with associated probabilities of being picked)
    """
    def biased_choice(self, **kwargs):
        if 'is_active' in kwargs:
            kwargs.pop('is_active')

        queryset = super(BiasedManager, self).get_query_set()\
            .filter(is_active=True, **kwargs)

        if not queryset.count():
            raise self.model.DoesNotExist

        calculations = queryset.aggregate(weight_sum=models.Sum('weight'))
#        banners = queryset.extra(select={'bias': 'weight/%i' % calculations['weight_sum']})
        banners = queryset

        return pick([(b, 1. * b.weight / calculations['weight_sum']) for b in banners])

    def biased_sample(self, count, **kwargs):
        if 'is_active' in kwargs:
            kwargs.pop('is_active')

        queryset = super(BiasedManager, self).get_query_set()\
            .filter(is_active=True, **kwargs)

        if not queryset.count():
            raise self.model.DoesNotExist

        calculations = queryset.aggregate(weight_sum=models.Sum('weight'))
#        banners = queryset.extra(select={'bias': 'weight/%i' % calculations['weight_sum']})
        banners = queryset

        l = [(b, 1. * b.weight / calculations['weight_sum']) for b in banners]

        if count > len(l):
            count = len(l)

        chosen = []
        while len(chosen) < count:
            chosen.append(pick(l))

        return chosen
