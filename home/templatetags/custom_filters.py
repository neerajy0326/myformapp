from django import template

register = template.Library()

@register.filter(name='is_video')
def is_video(value):
    video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.mpeg', '.mpg']
    return value.lower().endswith(tuple(video_extensions))