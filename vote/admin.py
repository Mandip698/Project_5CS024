from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin import AdminSite
# from .forms import CustomAdminAuthenticationForm
from .models import User, Poll, Options, UserVotes


admin.site.site_header = "Voteहालः"
admin.site.site_title = "Voteहालः Admin Area"
admin.site.index_title = "Voteहालः Admin Area"


# Inline for managing Options inside Poll
class OptionsInline(admin.TabularInline):
    model = Options
    extra = 2  # Default options shown when creating a poll

# Admin view for Poll to manage topics and options
class PollAdmin(admin.ModelAdmin):
    list_display = ('topic', 'start_date', 'end_date', 'status', 'created_by', 'updated_by', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at','created_by', 'updated_by')
    search_fields = ('topic', 'created_by')
    list_filter = ('status',)
    inlines = [OptionsInline]

    fieldsets = (
        (None, {
            'fields': ('topic', 'description', 'start_date', 'end_date', 'status', 'created_by', 'updated_by')
        }),
        
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
        
        # print("name:", request.user.name)
        # print("username:", request.user.username)
        # print("email:", request.user.email)OT
        # print("get_username:", request.user.get_username())


# Admin view for Options
class OptionsAdmin(admin.ModelAdmin):
    list_display = ('option_name', 'poll_id', 'created_by', 'updated_by', 'created_at')
    readonly_fields = ['created_at','created_by', 'updated_by']
    search_fields = ('option_name', 'poll_id__topic')
    list_filter = ('poll_id',)
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
        
        
# Registering the models
admin.site.register(User)
admin.site.register(Poll, PollAdmin)


 

# Admin view for User Votes
# class UserVotesAdmin(admin.ModelAdmin):
#     list_display = ('user_id', 'poll_id', 'option_id', 'timestamp')
#     search_fields = ('user_id__email', 'poll_id__topic', 'option_id__option_name')
#     list_filter = ('poll_id', 'option_id')

# admin.site.register(Options, OptionsAdmin)
# admin.site.register(UserVotes, UserVotesAdmin)

# class CustomAdminSite(AdminSite):
#     login_form = CustomAdminAuthenticationForm

# admin.site = CustomAdminSite()