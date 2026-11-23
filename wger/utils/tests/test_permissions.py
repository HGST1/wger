# Standard Library
from types import SimpleNamespace

# Django
from django.test import SimpleTestCase

# wger
from wger.utils.permissions import (
    CreateOnlyPermission,
    UpdateOnlyPermission,
    WgerPermission,
)


class PermissionTestCase(SimpleTestCase):
    def setUp(self):
        self.permission = WgerPermission()
        self.user = SimpleNamespace(is_authenticated=True)
        self.request = SimpleNamespace(user=self.user, method='GET')
        self.view = SimpleNamespace()

    def test_private_view_requires_authenticated_user(self):
        self.view.is_private = True

        self.assertTrue(self.permission.has_permission(self.request, self.view))

        self.request.user.is_authenticated = False
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_owner_can_use_any_method(self):
        owner = SimpleNamespace(user=self.user)
        obj = SimpleNamespace(get_owner_object=lambda: owner)
        self.request.method = 'POST'

        self.assertTrue(self.permission.has_object_permission(self.request, self.view, obj))

    def test_global_objects_are_read_only(self):
        obj = SimpleNamespace(get_owner_object=lambda: False)

        self.assertTrue(self.permission.has_object_permission(self.request, self.view, obj))

        self.request.method = 'POST'
        self.assertFalse(self.permission.has_object_permission(self.request, self.view, obj))

    def test_create_only_permission(self):
        permission = CreateOnlyPermission()

        for method in ('GET', 'HEAD', 'OPTIONS'):
            self.request.method = method
            self.assertTrue(permission.has_permission(self.request, self.view))

        self.request.method = 'POST'
        self.assertTrue(permission.has_permission(self.request, self.view))
        self.request.user.is_authenticated = False
        self.assertFalse(permission.has_permission(self.request, self.view))

    def test_update_only_permission_allows_patch_but_not_post(self):
        permission = UpdateOnlyPermission()

        self.request.method = 'PATCH'
        self.assertTrue(permission.has_permission(self.request, self.view))

        self.request.method = 'POST'
        self.assertFalse(permission.has_permission(self.request, self.view))
