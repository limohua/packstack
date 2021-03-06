"""
Installs and configures Glance
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import basedefs
import packstack.installer.common_utils as utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Glance"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Glance configuration")
    paramsList = [
                  {"CMD_OPTION"      : "glance-host",
                   "USAGE"           : "The IP address of the server on which to install Glance",
                   "PROMPT"          : "Enter the IP address of the Glance server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_GLANCE_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "glance-db-passwd",
                   "USAGE"           : "The password to use for the Glance to access DB",
                   "PROMPT"          : "Enter the password for the Glance DB access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_GLANCE_DB_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "glance-ks-passwd",
                   "USAGE"           : "The password to use for the Glance to authenticate with Keystone",
                   "PROMPT"          : "Enter the password for the Glance Keystone access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_GLANCE_KS_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "GLANCE",
                  "DESCRIPTION"           : "Glance Config parameters",
                  "PRE_CONDITION"         : "CONFIG_GLANCE_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    conf = controller.CONF
    if conf['CONFIG_GLANCE_INSTALL'] != 'y':
        if conf['CONFIG_NOVA_INSTALL'] == 'y':
            raise RuntimeError('Glance is required to install Nova properly. '
                               'Please set CONFIG_GLANCE_INSTALL=y')
        return

    glancesteps = [
             {'title': 'Adding Glance Keystone manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Adding Glance manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Glance", [], [], glancesteps)

def createkeystonemanifest():
    manifestfile = "%s_keystone.pp" % controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_glance.pp")
    appendManifestFile(manifestfile, manifestdata)

def createmanifest():
    manifestfile = "%s_glance.pp" % controller.CONF['CONFIG_GLANCE_HOST']
    manifestdata = getManifestTemplate("glance.pp")
    appendManifestFile(manifestfile, manifestdata)
