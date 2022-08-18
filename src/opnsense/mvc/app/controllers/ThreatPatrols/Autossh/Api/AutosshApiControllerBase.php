<?php

/*
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
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

use OPNsense\Core\Backend;
use OPNsense\Core\Config;
use OPNsense\Base\ApiControllerBase;

class AutosshApiControllerBase extends ApiControllerBase
{
    public function validate($model, $node = null, $reference = null)
    {
        $result = array('status' => 'fail', 'validations' => array());
        $validation_messages = $model->performValidation();
        foreach ($validation_messages as $field => $message) {
            if ($node != null) {
                $index = str_replace($node->__reference, $reference, $message->getField());
                $result['validations'][$index] = $message->getMessage();
            } else {
                $result['validations'][$message->getField()] = $message->getMessage();
            }
        }
        return $result;
    }

    public function configctlAction($action, $uuid)
    {
        $backend = new Backend();
        $configd_run = sprintf('autossh %s %s', escapeshellarg($action), escapeshellarg($uuid));
        return trim($backend->configdRun($configd_run));
    }

    public function save($model, $node = null, $reference = null)
    {
        $result = $this->validate($model, $node, $reference);
        if (0 === count($result['validations'])) {
            $model->serializeToConfig();
            Config::getInstance()->save();
            return $this->doConfigUpdates("Data saved");
        }
        return $result;
    }

    public function doConfigUpdates($message = null)
    {
        $backend = new Backend();

        // reload templates first
        $backend_response = trim($backend->configdRun('template reload ThreatPatrols/Autossh'));
        if (strtoupper($backend_response) !== 'OK') {
            return array(
                'status' => 'fail',
                'message' => 'Error while reloading autossh template files, review configd logs for more information'
            );
        }

        // render the autossh files
        $backend_response = @json_decode(trim($backend->configdRun('autossh config_helper')), true);
        if (empty($backend_response) || !isset($backend_response['status'])) {
            return array(
                'status' => 'fail',
                'message' => 'Error while performing autossh config_helper, review configd logs for more information'
            );
        }

        if (empty($message)) {
            $message = "Configuration template and configuration helper completed";
        }
        return array('status' => 'success',  'message' => $message);
    }

    public function afterExecuteRoute($dispatcher)
    {
        /**
         * In the limited situation of an "info" action with "html" we catch the regular
         * afterExecuteRoute() to prevent htmlspecialchars() being universally applied.
         */
        if ($dispatcher->getActionName() === "info") {
            $data = $dispatcher->getReturnedValue();
            if (is_array($data) && isset($data['html']) && true === $data['html']) {
                $this->response->setContentType('application/json', 'UTF-8');
                $this->response->setContent(json_encode($data));
                return $this->response->send();
            }
        }
        // all other situations get passed to the parent as usual.
        return parent::afterExecuteRoute($dispatcher);
    }
}
