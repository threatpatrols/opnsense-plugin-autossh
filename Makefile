PLUGIN_NAME=        autossh
PLUGIN_VERSION=     0.2.19
PLUGIN_COMMENT=     Create and automatically persist SSH based tunnels using autossh
PLUGIN_MAINTAINER=  contact@threatpatrols.com
PLUGIN_DEPENDS=     autossh

PLUGIN_PREFIX=      os-
PLUGIN_SUFFIX=
PLUGIN_DEVEL=       no
PLUGIN_WWW=         https://github.com/threatpatrols/opnsense-plugin-autossh

_VERSION_UPDATE!=   echo "__version__ = \"${PLUGIN_VERSION}\"" > src/opnsense/scripts/ThreatPatrols/Autossh/autossh/__version__.py

.include "../../Mk/plugins.mk"