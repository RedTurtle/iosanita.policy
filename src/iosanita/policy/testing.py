# -*- coding: utf-8 -*-
from iosanita.contenttypes.testing import TestLayer as ContentTypesTestLayer
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE
from zope.configuration import xmlconfig

import collective.feedback
import collective.volto.dropdownmenu
import collective.volto.enhancedlinks
import collective.volto.formsupport
import collective.volto.slimheader
import collective.volto.socialsettings
import collective.volto.subfooter
import iosanita.contenttypes
import iosanita.policy
import plone.app.caching
import souper.plone


class TestLayer(ContentTypesTestLayer):
    def setUpZope(self, app, configurationContext):
        super().setUpZope(app, configurationContext)
        self.loadZCML(package=plone.app.caching)
        self.loadZCML(package=iosanita.contenttypes)
        self.loadZCML(package=collective.volto.enhancedlinks)
        self.loadZCML(package=collective.feedback)
        self.loadZCML(package=souper.plone)
        self.loadZCML(package=collective.volto.slimheader)
        self.loadZCML(package=collective.volto.dropdownmenu)
        self.loadZCML(package=collective.volto.socialsettings)
        self.loadZCML(package=collective.volto.subfooter)
        self.loadZCML(package=collective.volto.formsupport)
        self.loadZCML(package=iosanita.policy, context=configurationContext)

        xmlconfig.file(
            "configure.zcml",
            iosanita.policy,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.caching:default")
        applyProfile(portal, "iosanita.policy:default")


FIXTURE = TestLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="IoSanitaPolicyLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name="IoSanitaPolicyLayer:FunctionalTesting",
)

RESTAPI_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="IoSanitaPolicyLayer:RestAPITesting",
)
