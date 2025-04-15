from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib import admin
from .models import User, Poll, Option, UserVote
import subprocess


admin.site.site_header = "Voteहालः"
admin.site.site_title = "Voteहालः Admin Area"
admin.site.index_title = "Voteहालः Admin Area"


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_active')
    change_list_template = "admin/user_import.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-users/', self.admin_site.admin_view(self.import_users), name="import_users"),
        ]
        return custom_urls + urls

    def import_users(self, request):
        try:
            result = subprocess.run(
                ["python", "manage.py", "import_users"],
                capture_output=True,
                text=True,
            )
    
            stdout_msg = result.stdout.strip()
            stderr_msg = result.stderr.strip()
    
            if result.returncode == 0:
                messages.success(request, stdout_msg or "Users imported successfully.")
            else:
                messages.error(request, stderr_msg or "Error importing users. Please check the logs.")
    
        except Exception as e:
            messages.error(request, f"Exception occurred while importing users: {str(e)}")
    
        return HttpResponseRedirect("../")




# Inline for managing Options inside Poll
class OptionsInline(admin.TabularInline):
    model = Option
    extra = 2  # Default options shown when creating a poll


# Admin view for Poll to manage topics and options
class PollAdmin(admin.ModelAdmin):
    list_display = ('topic', 'start_date', 'end_date', 'status', 'created_by', 'updated_by', 'created_on', 'updated_on')
    readonly_fields = ('created_on', 'updated_on','created_by', 'updated_by')
    search_fields = ('topic', 'created_by')
    list_filter = ('status',)
    inlines = [OptionsInline]

    fieldsets = (
        (None, {
            'fields': ('topic', 'description', 'start_date', 'end_date', 'status', 'created_by', 'updated_by')
        }),
        
        ('Date Information', {
            'fields': ('created_on', 'updated_on'),
            'classes': ('collapse',)
        })
    )
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
        
        
# Registering the models
admin.site.register(User, UserAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(UserVote)