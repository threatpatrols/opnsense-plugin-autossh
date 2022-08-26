PLUGIN_NAME=        autossh
PLUGIN_VERSION=     0.2.40
PLUGIN_COMMENT=     Create and automatically persist SSH based tunnels using autossh
PLUGIN_MAINTAINER=  contact@threatpatrols.com
PLUGIN_WWW=         https://documentation.threatpatrols.com/opnsense/plugins/autossh/
PLUGIN_DEPENDS=     autossh

PLUGIN_PREFIX=      os-
PLUGIN_SUFFIX=
PLUGIN_DEVEL=       no

_VERSION_UPDATE!=   echo "__version__ = \"${PLUGIN_VERSION}\"" > src/opnsense/scripts/ThreatPatrols/Autossh/autossh/__version__.py

.include "../../Mk/plugins.mk"
