from typing import List, Union
from appauto.operator.amaas_node import AMaaSNodeCli


class BaseDeploy(AMaaSNodeCli):
    def __init__(
        self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22, deploy_path="/mnt/data/deploy/"
    ):
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port)
        self.deploy_path = deploy_path

        self.ctn_names: Union[List, str] = None
        self.image_names: Union[List, str] = None

    def decompress(self, tar_name: str):
        cmd = f"cd {self.deploy_path} && sudo tar -zxvf {tar_name}"
        self.run(cmd, sudo=False)

    def have_tar(self, tar_name: str):
        return self.have_file(f"{self.deploy_path}{tar_name}")
