from django import template

register = template.Library()


@register.filter
def has_group(user, group_name):

    if user.is_superuser:
        return True

    return user.groups.filter(
        name=group_name
    ).exists()


@register.filter
def has_any_group(user, groups):

    if user.is_superuser:
        return True

    group_list = [
        g.strip()
        for g in groups.split(",")
    ]

    return user.groups.filter(
        name__in=group_list
    ).exists()