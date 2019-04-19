from ansible.plugins.callback import CallbackBase
import json
class DeployResultsCollector(CallbackBase):
    """
    直接执行模块命令的回调类
    """

    def __init__(self, sock, send_msg, *args, **kwargs):
        super(DeployResultsCollector, self).__init__(*args, **kwargs)
        self.sock = sock
        self.send_msg = send_msg

    def v2_runner_on_unreachable(self, result):
        if 'msg' in result._result:
            data = '<p style="color: #FF0000">\n主机{host}不可达！==> {stdout}\n剔除该主机！</p>'.format(
                host=result._host.name, stdout=result._result.get('msg'))
        else:
            data = '<p style="color: #FF0000">\n主机{host}不可达！==> {stdout}\n剔除该主机！</p>'.format(
                host=result._host.name, stdout=json.dumps(result._result, indent=4))

        self.chk_host_list(data, result._host.name)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        data = '<p style="color: #008000">\n主机{host}执行任务成功！\n</p>'.format(host=result._host.name)
        self.sock.send_save(data, send=self.send_msg)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'stderr' in result._result:
            data = '<p style="color: #FF0000">\n主机{host}执行任务失败 ==> {stdout}\n剔除该主机！</p>'.format(
                host=result._host.name, stdout=result._result.get('stderr').encode().decode('utf-8'))
        elif 'msg' in result._result:
            data = '<p style="color: #FF0000">\n主机{host}执行任务失败 ==> {stdout}\n剔除该主机！</p>'.format(
                host=result._host.name, stdout=result._result.get('msg'))
        else:
            data = '<p style="color: #FF0000">\n主机{host}执行任务失败 ==> {stdout}\n剔除该主机！</p>'.format(
                host=result._host.name, stdout=json.dumps(result._result, indent=4))
        self.chk_host_list(data, result._host.name)

    def chk_host_list(self, data, host):
        self.sock.send_save(data, send=self.send_msg)
        self.sock.host_list.remove(host)
        self.sock.host_fail.append(host)
        if len(self.sock.host_list) == 0:
            self.sock.send('<p style="color: #FF0000">所有主机均部署失败！退出部署流程！</p>', close=True)
            self.sock.deploy_results.append('<p style="color: #FF0000">所有主机均部署失败！退出部署流程！</p>')
