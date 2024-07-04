# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from iosanita.policy.testing import IOSANITA_POLICY_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that iosanita.policy is properly installed."""

    layer = IOSANITA_POLICY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if iosanita.policy is installed."""
        self.assertTrue(self.installer.is_product_installed("iosanita.policy"))

    def test_browserlayer(self):
        """Test that IIosanitaPolicyLayer is registered."""
        from iosanita.policy.interfaces import IIosanitaPolicyLayer
        from plone.browserlayer import utils

        self.assertIn(IIosanitaPolicyLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = IOSANITA_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("iosanita.policy")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if iosanita.policy is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("iosanita.policy"))

    def test_browserlayer_removed(self):
        """Test that IIosanitaPolicyLayer is removed."""
        from iosanita.policy.interfaces import IIosanitaPolicyLayer
        from plone.browserlayer import utils

        self.assertNotIn(IIosanitaPolicyLayer, utils.registered_layers())
