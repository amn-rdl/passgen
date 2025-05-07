from django.db import models
from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget

from simple_history.admin import SimpleHistoryAdmin

from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.paginator import InfinitePaginator
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User


class UserAdmin(ModelAdmin):
    list_display = ('username','last_name','first_name' ,'email')
    search_fields = ('username','last_name','first_name' ,'email')
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    actions_list = ["changelist_action"]

    @action(description=_("Changelist action"), url_path="changelist-action", permissions=["changelist_action"])
    def changelist_action(self, request: HttpRequest):
        return redirect(
          reverse_lazy("admin:users_user_changelist")
        )

    def has_changelist_action_permission(self, request: HttpRequest):
        return True

admin.site.unregister(Group)

User = get_user_model()

@admin.register(User)
class CustomAdminClass(SimpleHistoryAdmin, ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    compressed_fields = True
    warn_unsaved_form = True 
    readonly_preprocess_fields = {
        "model_field_name": "html.unescape",
        "other_field_name": lambda content: content.strip(),
    }
    list_filter_submit = False
    list_fullwidth = False
    list_filter_sheet = True
    list_horizontal_scrollbar_top = False
    list_disable_select_all = False
    change_form_show_cancel_button = True
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
        ArrayField: {
            "widget": ArrayWidget,
        }
    }

