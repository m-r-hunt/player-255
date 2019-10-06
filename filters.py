import django.template

register = django.template.Library()


def filter_name(kw):
    return kw.name


def filter_status(kw):
    return kw.name.capitalize()


def filter_remove_title_credits(list):
    out = []
    for s in list:
        splits = s.split("-")
        splits = [s for ss in splits for s in ss.split(".")]
        if "title" in splits or "credits" in splits:
            continue
        out.append(s)
    return out


def filter_has_credits(list):
    for s in list:
        splits = s.split("-")
        splits = [s for ss in splits for s in ss.split(".")]
        if "credits" in splits:
            return True
    return False


register.filter("name", filter_name)
register.filter("status", filter_status)
register.filter("remove_title_credits", filter_remove_title_credits)
register.filter("has_credits", filter_has_credits)
