# -*- coding: utf-8 -*-
from iosanita.contenttypes.testing import TestLayer as ContentTypesTestLayer
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE
from zope.configuration import xmlconfig

import collective.feedback
import collective.volto.enhancedlinks
import iosanita.contenttypes
import iosanita.policy
import redturtle.volto
import souper.plone


class TestLayer(ContentTypesTestLayer):
    def setUpZope(self, app, configurationContext):
        super().setUpZope(app, configurationContext)

        self.loadZCML(package=redturtle.volto)
        self.loadZCML(package=iosanita.contenttypes)
        self.loadZCML(package=collective.volto.enhancedlinks)
        self.loadZCML(package=collective.feedback)
        self.loadZCML(package=souper.plone)

        self.loadZCML(package=iosanita.policy, context=configurationContext)
        self.loadZCML(package=collective.taxonomy)
        xmlconfig.file(
            "configure.zcml",
            iosanita.policy,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
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
