# Autossh for OPNsense

The Autossh plugin for OPNsense is a wrapper for the autossh system-package that allows for establishing persistent reliable SSH tunnels with remote hosts. It can be used to solve a wide range of connection challenges through the (sometimes creative) use of TCP port-forwards.

Autossh tunnels can be used to quickly solve a wide range of challenges all over SSH, without the need for VPN clients etc:
 * Provide reverse-remote access to a site that has no public addresses, such as when ISPs use NAT.
 * Ensure redundant multipath reverse-remote access via both primary and secondary connections via interface binding.
 * Create your own "privacy" VPN system for local network users using a SOCKS proxy (ssh-dynamic-forward) to a remote system.
 * Provide local network access to remote system services such as SMTP relays or another remote TCP services.
 * Provide reverse-remote access to local network services such local RDP services.

## Documentation
 * https://documentation.threatpatrols.com/opnsense/plugins/autossh/

## Source
 * https://github.com/threatpatrols/opnsense-plugin-autossh

## Copyright
* Copyright &copy; 2022 Threat Patrols Pty Ltd &lt;contact@threatpatrols.com&gt;
* Copyright &copy; 2018 Verb Networks Pty Ltd &lt;contact@verbnetworks.com&gt;
* Copyright &copy; 2018 Nicholas de Jong &lt;me@nicholasdejong.com&gt;

All rights reserved.

## License
* BSD-2-Clause - see LICENSE file for full details.
