
PLUGIN_NAME=        autossh
PLUGIN_VERSION=     0.2.2
PLUGIN_COMMENT=     Create and automatically persist SSH based tunnels
PLUGIN_MAINTAINER=  contact@threatpatrols.com
PLUGIN_WWW=         https://github.com/threatpatrols/opnsense-plugin-autossh
PLUGIN_DEPENDS=     autossh

PLUGIN_PREFIX=		os-
PLUGIN_SUFFIX=
PLUGIN_DEVEL=       no

_VERSION_UPDATE!=   echo "__version__ = \"${PLUGIN_VERSION}\"" > src/opnsense/scripts/ThreatPatrols/Autossh/autossh/__version__.py

.include "../../Mk/plugins.mk"
