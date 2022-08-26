{#
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    Copyright (c) 2018 Verb Networks Pty Ltd <contact@verbnetworks.com>
    Copyright (c) 2018 Nicholas de Jong <me@nicholasdejong.com>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#}

<div class="alert alert-info hidden" role="alert" id="responseMsg"></div>
<div class="alert alert-info hidden" role="alert" id="applyChangesMessage">
   <button class="btn btn-primary pull-right" id="btnApplyChanges" type="button"><b>{{ lang._('Apply changes') }}</b> <i id="btnApplyChangesProgress"></i></button>
   {{ lang._('Configuration changed, please apply changes to reconfigure the Autossh service tunnels.')}}<br><br>
</div>

<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#tunnels">{{ lang._('Tunnels') }}</a></li>
    <li><a data-toggle="tab" href="#keys">{{ lang._('Keys') }}</a></li>
    <li><a data-toggle="tab" href="#about">{{ lang._('About') }}</a></li>
</ul>

<div class="tab-content content-box tab-content">
    
    <div id="tunnels" class="tab-pane fade in active">
        <table id="grid-tunnels" class="table table-condensed table-hover table-striped table-responsive" data-editDialog="DialogTunnels">

            <thead>
            <tr>
                <th data-column-id="enabled" data-width="6em" data-type="string" data-formatter="row_toggle">{{ lang._('Enabled') }}</th>
                <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{ lang._('Id') }}</th>
                <th data-column-id="description" data-type="string" data-visible="true">{{ lang._('Description') }}</th>
                <th data-column-id="connection" data-type="string" data-visible="true">{{ lang._('Connection') }}</th>
                <th data-column-id="local_forward" data-type="string" data-visible="true" data-formatter="code_wrap">{{ lang._('Local Forward') }}</th>
                <th data-column-id="dynamic_forward" data-type="string" data-visible="true" data-formatter="code_wrap">{{ lang._('Dynamic Forward') }}</th>
                <th data-column-id="remote_forward" data-type="string" data-visible="true" data-formatter="code_wrap">{{ lang._('Remote Forward') }}</th>
                <th data-column-id="commands" data-width="10em" data-formatter="tunnel_commands" data-sortable="false">{{ lang._('Commands') }}</th>
            </tr>
            </thead>

            <tbody></tbody>

            <tfoot>
            <tr>
                <td></td>
                <td>
                    <button data-action="add" type="button" class="btn btn-xs btn-default"><span class="fa fa-plus"></span></button>
                    <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"><span class="fa fa-trash-o"></span></button>
                </td>
            </tr>
            </tfoot>

        </table>
    </div>

    <div id="keys" class="tab-pane fade in">
        <table id="grid-keys" class="table table-condensed table-hover table-striped table-responsive" data-editDialog="DialogKeys">

            <thead>
            <tr>
                <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{ lang._('Id') }}</th>
                <th data-column-id="name" data-width="20em" data-type="string" data-visible="true">{{ lang._('Name') }}</th>
                <th data-column-id="description" data-type="string" data-visible="true">{{ lang._('Description') }}</th>
                <th data-column-id="key_fingerprint" data-type="string" data-visible="true">{{ lang._('SSH Key Fingerprint') }}</th>
                <th data-column-id="type" data-width="8em" data-type="string" data-visible="true">{{ lang._('Type') }}</th>
                <th data-column-id="timestamp" data-width="14em" data-type="string" data-visible="true">{{ lang._('Created') }}</th>
                <th data-column-id="commands" data-width="10em" data-formatter="key_commands" data-sortable="false">{{ lang._('Commands') }}</th>
            </tr>
            </thead>

            <tbody></tbody>

            <tfoot>
            <tr>
                <td></td>
                <td>
                    <button data-action="add" type="button" class="btn btn-xs btn-default"><span class="fa fa-plus"></span></button>
                    <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"><span class="fa fa-trash-o"></span></button>
                </td>
            </tr>
            </tfoot>

        </table>
    </div>
    
    <div id="about" class="tab-pane fade in">
        <div class="content-box" style="padding-bottom: 1.5em;">

            <div  class="col-md-12">
                <h1>Autossh</h1>
                <p>
                    The Autossh plugin for OPNsense is a wrapper for the autossh system-package that
                    allows for establishing persistent reliable SSH tunnels with remote hosts.
                    It can be used to solve a wide range of connection challenges through the (sometimes
                    creative) use of TCP port-forwards.
                </p>

                <p>
                    Autossh tunnels can be used to quickly solve a wide range of networking challenges without the need for additional VPN servers and clients:
                </p>
                <ul>
                    <li>Provide reverse-remote access to a site that has no public addresses, such as when ISPs use NAT.</li>
                    <li>Ensure redundant multipath reverse-remote access via both primary and secondary connections via interface binding.</li>
                    <li>Create your own "privacy" VPN system for local network users using a SOCKS proxy (ssh-dynamic-forward) to a remote system.</li>
                    <li>Provide local network access to remote system services such as SMTP relays or another remote TCP services.</li>
                    <li>Provide reverse-remote access to local network services such local RDP services.</li>
                </ul>

                <h2>Version</h2>
                <ul>
                    <li>{{ autossh_version }}</li>
                </ul>

                <hr />
                
                <h2>Documentation</h2>
                <ul>
                    <li><a rel="noreferrer noopener" target="_blank" href="https://documentation.threatpatrols.com/opnsense/plugins/autossh/">https://documentation.threatpatrols.com/opnsense/plugins/autossh</a></li>
                </ul>

                <h2>Issues</h2>
                <ul>
                    <li><a rel="noreferrer noopener" target="_blank" href="https://github.com/threatpatrols/opnsense-plugin-autossh/issues">https://github.com/threatpatrols/opnsense-plugin-autossh/issues</a></li>
                </ul>

                <h2>Source</h2>
                <ul>
                    <li><a rel="noreferrer noopener" target="_blank" href="https://github.com/threatpatrols/opnsense-plugin-autossh">https://github.com/threatpatrols/opnsense-plugin-autossh</a></li>
                </ul>

                <h2>Copyright</h2>
                <p>
                    Autossh (c) 2022 <a rel="noreferrer noopener" target="_blank" href="https://www.threatpatrols.com">Threat Patrols Pty Ltd</a>
                </p>
                <p>
                    All rights reserved.
                </p>

                <h2>License</h2>
                <p>BSD-2-Clause - see source LICENSE file for details.</p>

            </div>

        </div>
    </div>
</div>

{# include dialogs #}
{{ partial('layout_partials/base_dialog',['fields':formDialogKeys,'id':'DialogKeys','label':lang._('SSH key')])}}
{{ partial('layout_partials/base_dialog',['fields':formDialogTunnels,'id':'DialogTunnels','label':lang._('SSH tunnel')])}}

<style>
    div.modal-dialog div.bootstrap-dialog-message p {
        padding: 0.5em;
        border: 1px solid #999999;
        font-size: 100%;
        font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
        word-break: break-all;  
    }
</style>

<script>
    
$(document).ready(function() {

    $("#grid-tunnels").UIBootgrid(
        {   search:'/api/autossh/tunnels/search',
            get:'/api/autossh/tunnels/get/',
            set:'/api/autossh/tunnels/set/',
            add:'/api/autossh/tunnels/add/',
            del:'/api/autossh/tunnels/del/',
            info:'/api/autossh/tunnels/info/',
            toggle:'/api/autossh/tunnels/toggle/',

            options:{
                ajax: true,
                selection: true,
                multiSelect: true,
                rowCount:[10, 25, 100, -1] ,
                formatters:{
                    tunnel_commands: function(column, row) {
                        return '<button type="button" class="btn btn-xs btn-default command-info"   data-row-id="' + row.uuid + '"><span class="fa fa-key"></span></button> ' +
                               '<button type="button" class="btn btn-xs btn-default command-edit"   data-row-id="' + row.uuid + '"><span class="fa fa-pencil"></span></button> ' +
                               '<button type="button" class="btn btn-xs btn-default command-copy"   data-row-id="' + row.uuid + '"><span class="fa fa-clone"></span></button> ' +
                               '<button type="button" class="btn btn-xs btn-default command-delete" data-row-id="' + row.uuid + '"><span class="fa fa-trash-o"></span></button>';
                    },
                    row_toggle: function (column, row) {
                        if (parseInt(row[column.id], 2) === 1) {
                            return '<span style="cursor: pointer;" class="fa fa-check-square-o command-toggle" data-value="1" data-row-id="' + row.uuid + '"></span>';
                        } else {
                            return '<span style="cursor: pointer;" class="fa fa-square-o command-toggle" data-value="0" data-row-id="' + row.uuid + '"></span>';
                        }
                    },
                    code_wrap: function(column, row) {
                        if(row[column.id].length > 0) {
                            return '<code>' + $('<span/>', {'text': row[column.id]}).text() + '</code>';
                        }
                        return '';
                    },
                }
            },
        },
    );

    $("#grid-keys").UIBootgrid(
        {   search:'/api/autossh/keys/search',
            get:'/api/autossh/keys/get/',
            set:'/api/autossh/keys/set/',
            add:'/api/autossh/keys/add/',
            del:'/api/autossh/keys/del/',
            info:'/api/autossh/keys/info/',

            options:{
                ajax: true,
                selection: true,
                multiSelect: true,
                rowCount:[10, 25, 100, -1],
                formatters:{
                    key_commands: function (column, row) {
                        return '<button type="button" class="btn btn-xs btn-default command-info"   data-row-id="' + row.uuid + '"><span class="fa fa-key"></span></button> ' +
                               '<button type="button" class="btn btn-xs btn-default command-edit"   data-row-id="' + row.uuid + '"><span class="fa fa-pencil"></span></button> '+
                               '<button type="button" class="btn btn-xs btn-default command-delete" data-row-id="' + row.uuid + '"><span class="fa fa-trash-o"></span></button>';
                    }
                }
            },
        },
    );

    function setResponseMessageKeysCreate() {
        if ($('#grid-keys tbody tr').children().length <= 1) {
            $("#responseMsg").removeClass("hidden").removeClass("alert-danger").addClass('alert-info').html("{{ lang._('Please create an ssh-key before creating an ssh-tunnel.')}}");
        } else {
            $("#responseMsg").addClass("hidden");
        }
    }

    $('#btnApplyChanges').unbind('click').click(function(){
        $('#btnApplyChangesProgress').addClass('fa fa-spinner fa-pulse');
        ajaxCall(url='/api/autossh/service/reload', sendData={}, callback=function(data,status) {
            if (status === 'success') {
                $('#responseMsg').removeClass('hidden').html(data.message);
                $('#btnApplyChanges').blur();
                $('#applyChangesMessage').removeClass('hidden').addClass('hidden');
            }
            $('#btnApplyChangesProgress').removeClass('fa fa-spinner fa-pulse');
       });
    });

    $('#grid-keys').bootgrid().on('loaded.rs.jquery.bootgrid', setResponseMessageKeysCreate);

    $('#DialogKeys').change(function() {
        if($('#key\\.key_fingerprint').text().length >= 1) {
            $('#row_key\\.type div.btn-group button.dropdown-toggle').attr('data-toggle', '');
        } else {
            $('#row_key\\.type div.btn-group button.dropdown-toggle').attr('data-toggle', 'dropdown');
        }
    });

    formatTokenizersUI();
    // $('.selectpicker').selectpicker('refresh');

});
    
</script>
