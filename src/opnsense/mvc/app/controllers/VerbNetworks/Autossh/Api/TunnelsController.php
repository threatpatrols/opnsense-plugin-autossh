<?php

/*
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

namespace VerbNetworks\Autossh\Api;

use \OPNsense\Core\Backend;
use \OPNsense\Core\Config;
use \OPNsense\Base\ApiControllerBase;
use \OPNsense\Base\UIModelGrid;
use \VerbNetworks\Autossh\Autossh;

class TunnelsController extends ApiControllerBase
{
    
    public function searchAction()
    {
        $this->sessionClose(); // close out long running actions
        $model = new Autossh();
        $grid = new UIModelGrid($model->tunnels->tunnel);
        
        $grid_data = $grid->fetchBindRequest(
            $this->request,
            array('enabled', 'name', 'connection_string', 'connection_interface', 'ssh_key', 'local_forwards', 'remote_forwards'),
            'name'
        );
        return $grid_data;
    }

    public function getAction($uuid = null)
    {
        $model = new Autossh();
        if ($uuid != null) {
            $node = $model->getNodeByReference('tunnels.tunnel.'.$uuid);
            if ($node != null) {
                $data = $node->getNodes();
                return array('tunnel' => $data);
            }
        } else {
            $node = $model->tunnels->tunnel->add();
            return array('tunnel' => $node->getNodes());
        }
        return array();
    }
    
    public function infoAction($uuid = null)
    {
        $info = array(
            'title' => 'SSH tunnel connection authorized_key string',
            'message' => 'Unknown ssh-key',
        );
        if ($uuid != null) {
            $model = new Autossh();
            $node = $model->getNodeByReference('tunnels.tunnel.'.$uuid);
            if ($node != null) {
                $node_data = $node->getNodes();
                foreach($node_data['ssh_key'] as $ssh_key_uuid=>$ssh_key_attr) {
                    if((int)$ssh_key_attr['selected'] > 0 ) {
                        $ssh_key_node = $model->getNodeByReference('keys.key.'.$ssh_key_uuid);
                        $ssh_key_node_data = $ssh_key_node->getNodes();
                        $info['message'] = base64_decode($ssh_key_node_data['key_public']);
                        break;
                    }
                }
            }
        }
        return $info;
    }
    
    public function setAction($uuid = null)
    {
        $response = array(
            'status'=>'fail',
            'result'=>'failed',
            'message' => 'Invalid request'
        );
        if ($this->request->isPost() && $this->request->hasPost('tunnel')) {
            $model = new Autossh();
            if ($uuid != null) {
                $node = $model->getNodeByReference('tunnels.tunnel.'.$uuid);
                if ($node != null) {
                    $post_data = $this->request->getPost('tunnel');
                    $node->setNodes($post_data);
                    $response = $this->save($model, $node, 'tunnel');
                }
            }
        }
        return $response;
    }
    
    public function addAction()
    {
        $response = array(
            'status'=>'fail',
            'result'=>'failed',
            'message' => 'Invalid request'
        );
        if ($this->request->isPost() && $this->request->hasPost('tunnel')) {
            
            $model = new Autossh();
            $node = $model->tunnels->tunnel->add();
            $post_data = $this->request->getPost('tunnel');
            $node->setNodes($post_data);
            
            $validate = $this->validate($model, $node, 'tunnel');
            if (count($validate['validations']) == 0) {
                $response = $this->save($model, $node, 'tunnel');
            } else {
                $response['validations'] = $validate['validations'];
                $response['message'] = 'Validation errors';
            }
        }
        return $response;
    }
    
    public function delAction($uuid = null)
    {
        $response = array(
            'status'=>'fail',
            'result'=>'failed',
            'message' => 'Invalid request'
        );
        if ($this->request->isPost()) {
            $model = new Autossh();
            if ($uuid != null) {
                if ($model->tunnels->tunnel->del($uuid)) {
                    $model->serializeToConfig();
                    Config::getInstance()->save();
                    $response['result'] = 'deleted';
                    $response['message'] = 'Okay, item deleted';
                } else {
                    $response['result'] = 'not found';
                    $response['message'] = 'Failed to delete item';
                }
            }
        }
        return $response;
    }
    
    public function toggleAction($uuid = null)
    {
        $response = array(
            'status'=>'fail',
            'result'=>'failed',
            'message' => 'Invalid request'
        );
        if ($this->request->isPost()) {
            $model = new Autossh();
            if ($uuid != null) {
                $node = $model->getNodeByReference('tunnels.tunnel.'.$uuid);
                if ($node != null) {
                    $node_data = $node->getNodes();
                    $toggle_data = array(
                        'enabled' => ((int)$node_data['enabled'] > 0 ? 0 : 1)
                    );
                    $node->setNodes($toggle_data);
                    $response = $this->save($model, $node, 'tunnel');
                }
            }
        }
        return $response;
    }
    
    public function testAction()
    {
        $response = array();
        return $response;
    }
    
    private function save($model, $node = null, $reference = null)
    {
        $result = $this->validate($model, $node, $reference);
        if (count($result['validations']) == 0) {
            $model->serializeToConfig();
            Config::getInstance()->save();
            $result["status"] = "success";
            $result["result"] = "saved";
            unset($result["validations"]);
        }
        return $result;
    }
    
    private function validate($model, $node = null, $reference = null)
    {
        $result = array("status"=>"fail","validations" => array());
        $validation_messages = $model->performValidation();
        foreach ($validation_messages as $field => $message) {
            if ($node != null) {
                $index = str_replace($node->__reference, $reference, $message->getField());
                $result["validations"][$index] = $message->getMessage();
            } else {
                $result["validations"][$message->getField()] = $message->getMessage();
            }
        }
        return $result;
    }
}
