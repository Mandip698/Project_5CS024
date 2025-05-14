import sys
import subprocess
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib import admin
from .models import User, Poll, Option, UserVote


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
                [sys.executable, "manage.py", "import_users"],
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
    extra = 1  # Default options shown when creating a poll
    def has_add_permission(self, request, obj):
        if obj:  # If editing an existing Poll
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if obj:  # Editing existing Poll — disallow option changes
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False  # Always prevent deleting options in admin


# Admin view for Poll to manage topics and options
class PollAdmin(admin.ModelAdmin):
    # Fields to show in the admin list view for polls
    list_display = ('topic', 'start_date', 'end_date', 'status', 'created_by', 'updated_by', 'created_on', 'updated_on')
    # Fields that are always read-only in the form
    readonly_fields = ('created_on', 'updated_on','created_by', 'updated_by')
    # Allow admin to search polls by topic or who created it
    search_fields = ('topic', 'created_by__username','status')
    # Add filter options for the 'status' field
    list_filter = ('status','created_by__username')
    # Allow editing poll options inline (related model)

    inlines = [OptionsInline]
     # Organize the form fields into sections in the admin panel
    fieldsets = (
        (None, {
            'fields': ('topic', 'description', 'start_date', 'end_date', 'status', 'created_by', 'updated_by')
        }),
        
        ('Date Information', {
            'fields': ('created_on', 'updated_on'),
            'classes': ('collapse',)
        })
    )
    # Always read-only fields
    base_readonly = ('created_on', 'updated_on', 'created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.status == 'closed':
                # All fields readonly
                return [field.name for field in self.model._meta.fields]
            else:
                # Only allow 'status' field to be editable
                all_fields = [field.name for field in self.model._meta.fields]
                return list(set(all_fields) - {'status'})
        return self.base_readonly

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if obj:
            extra_context = extra_context or {}
            if obj.status == 'closed':
                extra_context['show_save'] = False
                extra_context['show_save_and_continue'] = False
                extra_context['show_save_and_add_another'] = False
                messages.warning(request, "This poll is closed and cannot be edited.")
            else:
                messages.info(request, "Only the poll status can be modified.")
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    # Optional: Prevent deletion if poll is live
    # def has_delete_permission(self, request, obj=None):
    #     if obj and obj.status == 'live':
    #         return False
    #     return super().has_delete_permission(request, obj)

        
# Registering the models
admin.site.register(User, UserAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(UserVote)