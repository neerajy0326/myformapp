from django import template
from django.utils import timezone
register = template.Library()

@register.filter(name='is_video')
def is_video(value):
    video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.mpeg', '.mpg']
    return value.lower().endswith(tuple(video_extensions))

@register.filter
def localtime(value, timezone_name='Asia/Kolkata'):
    if timezone_name:
        return timezone.localtime(value, timezone_name)
    else:
        return timezone.localtime(value)