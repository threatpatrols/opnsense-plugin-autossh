<?php

/*
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
*/

namespace ThreatPatrols\Autossh\Api;

use OPNsense\Core\Config;
use OPNsense\Base\UIModelGrid;
use ThreatPatrols\Autossh\Autossh;
use ThreatPatrols\Autossh\Api\AutosshApiControllerBase;

class TunnelsController extends AutosshApiControllerBase
{
    public function searchAction()
    {
        $this->sessionClose(); // close out long running actions
        $model = new Autossh();
        $grid = new UIModelGrid($model->tunnels->tunnel);

        $grid_data = $grid->fetchBindRequest(
            $this->request,
            array(
                'enabled', 'description', 'user', 'hostname', 'port', 'bind_interface', 'ssh_key',
                'local_forward', 'remote_forward', 'dynamic_forward'
            ),
            'hostname'
        );

        if (isset($grid_data['rows'])) {
            foreach ($grid_data['rows'] as $index => $tunnel) {
                $grid_data['rows'][$index]['connection'] = $tunnel['user'] . '@' . $tunnel['hostname'];
                if (!empty($tunnel['port'])) {
                    $grid_data['rows'][$index]['connection'] =
                         $grid_data['rows'][$index]['connection'] . ':' . $tunnel['port'];
                }
            }
        }
        return $grid_data;
    }

    public function getAction($uuid = null)
    {
        $model = new Autossh();
        if ($uuid != null) {
            $node = $model->getNodeByReference('tunnels.tunnel.' . $uuid);
            if ($node != null) {
                $data = array('tunnel' => $node->getNodes());
                return $data;
            }
        } else {
            $node = $model->tunnels->tunnel->add();
            $data = array('tunnel' => $node->getNodes());
            $data['tunnel']['known_host'] = 'new connection, no known host value';
            return $data;
        }
        return array();
    }

    public function infoAction($uuid = null)
    {
        $info = array(
            'title' => 'SSH server known host keys',
            'message' => null,
        );
        if ($uuid != null) {
            $response = json_decode($this->configctlAction("host_keys", $uuid), true);
            if ($response['status'] === 'success' && isset($response['data']) && count($response['data']) > 0) {
                $info['html'] = true; // required for afterExecuteRoute() trap
                $info['message'] = '';
                foreach ($response['data'] as $key_value) {
                    $info['message'] = $info['message'] . '<p>' . htmlspecialchars($key_value) . '</p>';
                }
            } else {
                $info['message'] = $response['message'];
            }
        }
        return $info;
    }

    public function setAction($uuid = null)
    {
        $response = array(
            'status' => 'fail',
            'message' => 'Invalid request'
        );
        if ($this->request->isPost() && $this->request->hasPost('tunnel')) {
            $model = new Autossh();
            if ($uuid !== null) {
                $node = $model->getNodeByReference('tunnels.tunnel.' . $uuid);
                if ($node !== null) {
                    $post_data = $this->request->getPost('tunnel');
                    $node->setNodes($post_data);
                    $response = $this->save($model, $node, 'tunnel');
                    if (1 === (int)$post_data['enabled']) {
                        $this->restartTunnel($uuid);
                    } else {
                        $this->stopTunnel($uuid);
                    }
                    return $response;
                }
            }
        }
        return $response;
    }

    public function addAction()
    {
        $response = array(
            'status' => 'fail',
            'message' => 'Invalid request'
        );
        if ($this->request->isPost() && $this->request->hasPost('tunnel')) {
            $model = new Autossh();
            $node = $model->tunnels->tunnel->add();
            $post_data = $this->request->getPost('tunnel');
            $node->setNodes($post_data);

            $validate = $this->validate($model, $node, 'tunnel');
            if (0 === count($validate['validations'])) {
                return $this->save($model, $node, 'tunnel');
            } else {
                return array(
                    'status' => 'fail',
                    'validations' => $validate['validations'],
                    'message' => 'Validation errors'
                );
            }
        }
        return $response;
    }

    public function delAction($uuid = null)
    {
        $response = array(
            'status' => 'fail',
            'message' => 'Invalid request'
        );
        if ($this->request->isPost()) {
            $model = new Autossh();
            if ($uuid != null) {
                $this->stopTunnel($uuid);
                if ($model->tunnels->tunnel->del($uuid)) {
                    $model->serializeToConfig();
                    Config::getInstance()->save();
                    return $this->doConfigUpdates("Item deleted");
                } else {
                    return array('status' => 'fail', 'message' => 'Item not found, nothing deleted');
                }
            }
        }
        return $response;
    }

    public function toggleAction($uuid = null)
    {
        $response = array(
            'status' => 'fail',
            'message' => 'Invalid request'
        );
        if ($this->request->isPost()) {
            $model = new Autossh();
            if ($uuid != null) {
                $node = $model->getNodeByReference('tunnels.tunnel.' . $uuid);
                if (!empty($node)) {
                    $node_data = $node->getNodes();
                    $toggle_data = array(
                        'enabled' => ((int)$node_data['enabled'] > 0 ? '0' : '1')
                    );
                    $node->setNodes($toggle_data);
                    $response = $this->save($model, $node, 'tunnel');
                    if (1 === (int)$toggle_data['enabled']) {
                        $this->startTunnel($uuid);
                    } else {
                        $this->stopTunnel($uuid);
                    }
                    return $response;
                }
            }
        }
        return $response;
    }

    public function startTunnel($uuid)
    {
        return $this->configctlAction("start_tunnel", $uuid);
    }

    public function restartTunnel($uuid)
    {
        return $this->configctlAction("restart_tunnel", $uuid);
    }

    public function stopTunnel($uuid)
    {
        return $this->configctlAction("stop_tunnel", $uuid);
    }
}
