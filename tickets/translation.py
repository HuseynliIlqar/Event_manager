from modeltranslation.translator import register, TranslationOptions
from .models import Event, EventCategory

@register(EventCategory)
class EventCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Event)
class EventTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'location') 