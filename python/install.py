#!python3
'''
    Simple installer script for making the Python implementation run as a service on the current host

    Copyright 2018 Jacques Gasselin

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import sys
import os

serverScriptPath = os.path.realpath(os.path.join(os.path.curdir, 'multiplay', 'simple_http_server.py'))

service = '''
[Unit]
Description=multiplay
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 %s
StandardInput=tty-force

[Install]
WantedBy=multi-user.target

''' % (serverScriptPath)

#must be run as 'sudo'
with open("/lib/systemd/system/multiplay.service", "wb") as f:
    f.write(service.encode())
    f.flush()
os.system('systemctl daemon-reload')
os.system('systemctl enable multiplay.service')
os.system('systemctl start multiplay.service')
