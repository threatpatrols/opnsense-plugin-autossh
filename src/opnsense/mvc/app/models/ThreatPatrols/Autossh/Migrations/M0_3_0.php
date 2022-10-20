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

namespace ThreatPatrols\Autossh\Migrations;

use OPNsense\Base\FieldTypes\BaseField;
use OPNsense\Core\Config;
use OPNsense\Base\BaseModelMigration;
use ThreatPatrols\Autossh\Autossh;

class M0_3_0 extends BaseModelMigration
{
    /**
     * Migrate incorrectly stored settings
     * @param AutoSSH $model
     */
    public function post($model)
    {
        $sshCiphers = array(
            "ciphers_01" => "chacha20-poly1305@openssh.com",
            "ciphers_02" => "aes128-ctr",
            "ciphers_03" => "aes192-ctr",
            "ciphers_04" => "aes256-ctr",
            "ciphers_05" => "aes128-gcm@openssh.com",
            "ciphers_06" => "aes256-gcm@openssh.com"
        );
        $sshHostKex = array(
            "host_key_algorithms_01" => "ecdsa-sha2-nistp256-cert-v01@openssh.com",
            "host_key_algorithms_02" => "ecdsa-sha2-nistp384-cert-v01@openssh.com",
            "host_key_algorithms_03" => "ecdsa-sha2-nistp521-cert-v01@openssh.com",
            "host_key_algorithms_04" => "ssh-ed25519-cert-v01@openssh.com",
            "host_key_algorithms_05" => "ssh-rsa-cert-v01@openssh.com",
            "host_key_algorithms_06" => "ecdsa-sha2-nistp256",
            "host_key_algorithms_07" => "ecdsa-sha2-nistp384",
            "host_key_algorithms_08" => "ecdsa-sha2-nistp521",
            "host_key_algorithms_09" => "ssh-ed25519",
            "host_key_algorithms_10" => "ssh-rsa"
        );
        $sshKex = array(
            "kex_algorithms_01" => "curve25519-sha256",
            "kex_algorithms_02" => "curve25519-sha256",
            "kex_algorithms_03" => "ecdh-sha2-nistp256",
            "kex_algorithms_04" => "ecdh-sha2-nistp384",
            "kex_algorithms_05" => "ecdh-sha2-nistp521",
            "kex_algorithms_06" => "diffie-hellman-group-exchange-sha256",
            "kex_algorithms_07" => "diffie-hellman-group16-sha512",
            "kex_algorithms_08" => "diffie-hellman-group18-sha512",
            "kex_algorithms_09" => "diffie-hellman-group-exchange-sha1",
            "kex_algorithms_10" => "diffie-hellman-group14-sha256",
            "kex_algorithms_11" => "diffie-hellman-group14-sha1"
        );
        $sshMacs = array(
            "macs_01" => "umac-64-etm@openssh.com",
            "macs_02" => "umac-128-etm@openssh.com",
            "macs_03" => "hmac-sha2-256-etm@openssh.com",
            "macs_04" => "hmac-sha2-512-etm@openssh.com",
            "macs_05" => "hmac-sha1-etm@openssh.com",
            "macs_06" => "umac-64@openssh.com",
            "macs_07" => "umac-128@openssh.com",
            "macs_08" => "hmac-sha2-256",
            "macs_09" => "hmac-sha2-512",
            "macs_10" => "hmac-sha1"
        );
        $sshKeyTypes = array(
            "pubkey_accepted_key_types_01" => "ecdsa-sha2-nistp256-cert-v01@openssh.com",
            "pubkey_accepted_key_types_02" => "ecdsa-sha2-nistp384-cert-v01@openssh.com",
            "pubkey_accepted_key_types_03" => "ecdsa-sha2-nistp521-cert-v01@openssh.com",
            "pubkey_accepted_key_types_04" => "ssh-ed25519-cert-v01@openssh.com",
            "pubkey_accepted_key_types_05" => "ssh-rsa-cert-v01@openssh.com",
            "pubkey_accepted_key_types_06" => "ecdsa-sha2-nistp256",
            "pubkey_accepted_key_types_07" => "ecdsa-sha2-nistp384",
            "pubkey_accepted_key_types_08" => "ecdsa-sha2-nistp521",
            "pubkey_accepted_key_types_09" => "ssh-ed25519",
            "pubkey_accepted_key_types_10" => "ssh-rsa"
        );
        $sshRekeyLimits = array(
            "rekey_limit_01" => "default none",
            "rekey_limit_02" => "1G 1h",
            "rekey_limit_03" => "1G 4h",
            "rekey_limit_04" => "1G 8h",
            "rekey_limit_05" => "2G 1h",
            "rekey_limit_06" => "2G 4h",
            "rekey_limit_07" => "2G 8h",
            "rekey_limit_08" => "4G 1h",
            "rekey_limit_09" => "4G 4h",
            "rekey_limit_10" => "4G 8h"
        );
        $cfgObj = Config::getInstance()->object();
        if (!isset($cfgObj->ThreatPatrols->Autossh->tunnels->tunnel)) {
            return;
        }
        foreach ($cfgObj->ThreatPatrols->Autossh->tunnels->tunnel as $tunnel) {
            foreach (explode(',',$tunnel->ciphers) as $cipher) {
                $newCiphers[] = $sshCiphers[$cipher];
            }
            $tunnel->ciphers = implode(',',$newCiphers);
            foreach (explode(',',$tunnel->host_key_algorithms) as $hostkex) {
                $newHostKex[] = $sshHostKex[$hostkex];
            }
            $tunnel->host_key_algorithms = implode(',',$newHostKex);
            foreach (explode(',',$tunnel->kex_algorithms) as $kex) {
                $newKex[] = $sshKex[$kex];
            }
            $tunnel->kex_algorithms = implode(',',$newKex);
            foreach (explode(',',$tunnel->macs) as $mac) {
                $newMacs[] = $sshMacs[$mac];
            }
            $tunnel->macs = implode(',',$newMacs);
            foreach (explode(',',$tunnel->pubkey_accepted_key_types) as $pubkeytype) {
                $newKeyTypes[] = $sshKeyTypes[$pubkeytype];
            }
            $tunnel->pubkey_accepted_key_types = implode(',',$newKeyTypes);
            foreach (explode(',',$tunnel->rekey_limit) as $pubkeytype) {
                $newKeyTypes[] = $sshKeyTypes[$pubkeytype];
            }
            $tunnel->pubkey_accepted_key_types = implode(',',$newKeyTypes);
            $rekeyLimit = (string)$tunnel->rekey_limit;
            $tunnel->rekey_limit = $sshRekeyLimits[$rekeyLimit];
        }
        // perform validation on the data in our model
        $validationMessages = $model->performValidation();
        foreach ($validationMessages as $messsage) {
            echo "validation failure on field ". $messsage->getField()."  returning message : ". $messsage->getMessage()."\n";
        }
    }
}
