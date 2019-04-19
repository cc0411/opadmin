# -*- coding: utf-8 -*-
from channels import  route_class
from webterminal.consumers import Webterminal,SshTerminalMonitor, BatchCommandExecute
from ansible_task.consumers import AnsModuleConsumer,AnsPlaybookConsumer
channel_routing = [
    route_class(Webterminal,path = r'^/ws/webssh/'),
    route_class(AnsModuleConsumer ,path=r'^/ws/adhocrun/' ),
    route_class(AnsPlaybookConsumer, path=r'^/ws/playbookrun/'),
    route_class(SshTerminalMonitor, path=r'^/monitor/(?P<channel>[\w-]+)'),
    route_class(BatchCommandExecute, path=r'^/batchexecute/'),
]