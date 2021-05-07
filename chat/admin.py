from django.contrib import admin

from chat.models import Message, Thread


class MessageInline(admin.StackedInline):
    model = Message
    fields = ('sender', 'text', 'date_sent')
    readonly_fields = ('sender', 'text', 'date_sent')


class ThreadAdmin(admin.ModelAdmin):
    model = Thread
    inlines = (MessageInline,)

admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message)
