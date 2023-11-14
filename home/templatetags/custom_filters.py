from django import template
from django.utils import timezone
from datetime import timedelta
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




register = template.Library()

@register.filter(name='dict_key')
def dict_key(d, k):
    return d.get(k, None)


@register.filter(name='format_last_active')
def format_last_active(last_active):
    now = timezone.now()

    if last_active is None:
        return "inactive"

    elapsed_time = now - last_active

    if elapsed_time < timedelta(seconds=10):
        return "active now"
    elif elapsed_time < timedelta(seconds=20):
        return "active just now"
    elif elapsed_time < timedelta(minutes=1):
        seconds = elapsed_time.seconds
        return f"active {seconds} seconds ago"
    elif elapsed_time < timedelta(hours=1):
        minutes = int(elapsed_time.total_seconds() // 60)
        return f"active {minutes} mins ago"
    elif elapsed_time < timedelta(days=1):
        hours = int(elapsed_time.total_seconds() // 3600)
        return f"active {hours} hours ago"
    else:
        days = elapsed_time.days
        return f"active {days} days ago"    