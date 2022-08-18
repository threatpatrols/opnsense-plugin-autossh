#!/bin/bash

#
#    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without modification,
#    are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
#    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

set -e

remote_address=${1}
remote_default_user="root"
action=${2}

if [ -z "${remote_address}" ] || [ -z "${action}" ]; then
    echo 'usage: '${0}' <remote-user@remote-host|remote-host> <install|uninstall>'
    exit 1
fi

if [[ ${remote_address} = *"@"* ]]; then
    remote="${remote_address}"
else
    remote="${remote_default_user}@${remote_address}"
fi

ssh_options="-o ControlMaster=auto -o ControlPersist=60s -q"
local_base_path=$(realpath $(dirname ${0})/../src/)
remote_base_path="/usr/local"

# =============================================================================

echo
echo "Variable settings"
echo "==="
echo "remote:                 ${remote}"
echo "action:                 ${action}"
echo "ssh_options:            ${ssh_options}"
echo "local_base_path:        ${local_base_path}"
echo "remote_base_path:       ${remote_base_path}"
echo

# =============================================================================

dev_install()
{

  # deploy_files
  echo "Deploy autossh files"
  echo "==="
  cd "${local_base_path}"
  for filepath_find in $(find . -type f -not -path */.py* -not -name *.pyc -not -name test_* -not -name .git*); do
      filepath=$(echo $filepath_find | sed 's/^..//')
      deploy_file "${local_base_path}/${filepath}" "${remote_base_path}/${filepath}"
  done
  echo

  echo "Rebuild the Autossh templates"
  echo "==="
  ssh ${ssh_options} ${remote} "configctl template reload ThreatPatrols/Autossh"
  echo

  echo "Restart OPNsense configd"
  echo "==="
  ssh ${ssh_options} ${remote} "/usr/local/etc/rc.configure_plugins; service configd restart"
  echo
}

# =============================================================================

dev_uninstall()
{
  echo "Remove autossh files"
  echo "==="
  cd "${local_base_path}"
  for filepath_find in $(find . -type f -not -path */.py* -not -name *.pyc -not -name test_* -not -name .git*); do
      filepath=$(echo $filepath_find | sed 's/^..//')
      remove_file "${remote_base_path}/${filepath}"
  done
  echo

  echo "Restart OPNsense configd"
  echo "==="
  ssh ${ssh_options} ${remote} "/usr/local/etc/rc.configure_plugins; service configd restart"
  echo
}

# =============================================================================

deploy_file()
{
  local src_fullpath=${1}
  local dst_fullpath=${2}
  echo "deploy: ${src_fullpath/${local_base_path}\//\{base\}/}"
  ssh ${ssh_options} "${remote}" "mkdir -p \"\`dirname ${dst_fullpath}\`\""
  scp ${ssh_options} -p "${src_fullpath}" "${remote}:${dst_fullpath}"
}

# =============================================================================

remove_file()
{
    local dst_fullpath=${1}
    if [[ "${dst_fullpath}" == *"Autossh"* ]]; then
      echo "remove-path: ${dst_fullpath}"
      ssh ${ssh_options} "${remote}" "rm -Rf \"\`dirname ${dst_fullpath}\`\""
    else
      echo "remove-file: ${dst_fullpath}"
      ssh ${ssh_options} "${remote}" "rm -f ${dst_fullpath}"
    fi
}

# =============================================================================

if [[ "${action}" = "install" ]]; then
    dev_install
    exit 0
elif [[ "${action}" = "uninstall" ]]; then
    dev_uninstall
    exit 0
fi

echo "ERROR: unknown action"
exit 1
