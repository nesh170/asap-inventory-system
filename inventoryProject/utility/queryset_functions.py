from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        return None


def get_or_not_found(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        raise NotFound(detail="{model_name} not found".format(model_name=model.__name__))

