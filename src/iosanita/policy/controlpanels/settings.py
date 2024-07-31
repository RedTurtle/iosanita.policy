# -*- coding: utf-8 -*-
from iosanita.policy import _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels.interfaces import IControlpanel
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import List
from zope.schema import SourceText
from zope.schema import TextLine


class IoSanitaSettingsControlpanel(IControlpanel):
    """ """


class IIoSanitaSettings(Interface):
    lead_image_dimension = List(
        title=_(
            "lead_image_dimension_label",
            default="Dimensioni lead image",
        ),
        description=_(
            "lead_image_dimension_help",
            default="Se un content-type deve avere una dimensione della "
            "leadimage particolare, indicarle qui. "
            "Inserire le dimensioni nella forma di esempio "
            "PortalType|900x900",
        ),
        required=True,
        default=[
            "News Item|1920x600",
            "Servizio|1920x600",
            "UnitaOrganizzativa|1920x600",
            "Persona|180x100",
        ],
        value_type=TextLine(),
    )

    search_sections = SourceText(
        title=_("search_sections_label", default="Sezioni ricerca"),
        description=_(
            "search_sections_help",
            default="Inserire una lista di sezioni per la ricerca.",
        ),
        default="",
        required=False,
    )

    show_modified_default = Bool(
        title=_("show_modified_default_label", default="Mostra la data di modifica"),
        description=_(
            "show_modified_default_help",
            default="Questo è il valore di default per decidere se mostrare "
            "o meno la data di modifica nei contenuti che hanno la behavior "
            "abilitata. E' poi possibile sovrascrivere il default nei singoli "
            'contenuti (nel tab "Impostazioni").',
        ),
        default=True,
        required=False,
    )

    show_dynamic_folders_in_footer = Bool(
        title=_("show_dynamic_folders_in_footer_label", default="Footer dinamico"),
        description=_(
            "show_dynamic_folders_in_footer_help",
            default="Se selezionato, il footer verrà popolato automaticamente "
            "con i contenuti di primo livello non esclusi dalla navigazione.",
        ),
        default=True,
        required=False,
    )

    contatti_testata = SourceText(
        title=_("contatti_testata_label", default="Contatti in testata"),
        description=_(
            "contatti_testatas_help",
            default="Inserire i contatti.",
        ),
        default="",
        required=False,
    )


class IoSanitaControlPanelForm(RegistryEditForm):
    schema = IIoSanitaSettings
    id = "io-sanita-control-panel"
    label = _("Impostazioni IoSanita")


class IoSanitaControlPanelView(ControlPanelFormWrapper):
    """ """

    form = IoSanitaControlPanelForm