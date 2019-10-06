import django.template

register = django.template.Library()


def filter_name(kw):
    return kw.name


register.filter("name", filter_name)
