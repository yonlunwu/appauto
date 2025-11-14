import json
from typing import Dict, Literal
from appauto.manager.connection_manager.http import HttpClient
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


class LarkClient(HttpClient):
    def __init__(
        self,
        headers=None,
        verify=False,
        app_id: str = "cli_a8b5109485f1100c",
        app_secret: str = "YKHxKdlW65z0jTwdXueGscbNjwa2ZE5L",
    ):
        super().__init__(headers, verify)
        self.headers = {"Authorization": f"Bearer {self.token(app_id, app_secret)}"}

    def token(self, app_id: str, app_secret: str) -> str:
        """获取 app_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        params = {"app_id": app_id, "app_secret": app_secret}
        res = self.request("post", url, data=params, timeout=30, check=False)
        return res.app_access_token

    def send_msg(self, payload: Dict, dst: Literal["dm", "group"]):
        dst_map = {"dm": "open_id", "group": "chat_id"}
        try:
            url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={dst_map.get(dst)}"
            self.post(url, json_data=payload, headers=self.headers, check=False)
        except Exception as e:
            logger.error(f"send dm msg failed: {e}")

    def msg_title_card(self, template: Literal["green", "red"]):
        return {
            "template": template,
            "title": {"content": "Test Passed" if template == "green" else "Test Failed", "tag": "plain_text"},
        }

    def msg_topic_card(self, topic: str):
        return {"tag": "div", "text": {"tag": "lark_md", "content": f"**🎯 Test Topic**\n {topic}"}}

    def msg_env_card(self, env_summary: Dict):
        return {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**🧪 Test Env**\n {self.convert_dict_to_md_code_block(env_summary)}",
            },
        }

    def msg_summary_card(self, summary_result: Dict):
        return {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📊 Test Summary**\n {self.convert_dict_to_md_code_block(summary_result)}",
            },
        }

    def msg_report_card(self, link: str = None):
        return {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"content": "📄 点击查看测试报告", "tag": "plain_text"},
                    "type": "primary",
                    # TODO
                    "url": link or "http://192.168.110.11:8090/autotest/test_reports/",
                }
            ],
        }

    def set_template(self, summary_result: Dict) -> Literal["red", "green"]:
        """有失败用红色, 全部通过用绿色"""
        return (
            "red"
            if any(
                [
                    summary_result.get("FAILED", None),
                    summary_result.get("XPASS", None),
                    summary_result.get("XFAIL", None),
                ]
            )
            else "green"
        )

    def construct_msg_payload(
        self,
        receive_id: str,
        result_summary: Dict,
        env_summary: Dict,
        link: str = None,
        topic: str = None,
        report_card=True,
    ):
        """
        发 dm 用 open_id; 发 group 用 chat_id(并且机器人要在 group 中)
        """
        elements = [
            self.msg_env_card(env_summary),
            self.msg_summary_card(result_summary),
        ]
        if report_card:
            elements.append(self.msg_report_card(link))
        if topic:
            elements.insert(0, self.msg_topic_card(topic))

        return {
            "receive_id": receive_id,
            "msg_type": "interactive",
            "content": json.dumps(
                {
                    "config": {"wide_screen_mode": True},
                    # 标题栏
                    "header": self.msg_title_card(template=self.set_template(result_summary)),
                    # 内部元素
                    "elements": elements,
                }
            ),
        }

    @staticmethod
    def convert_dict_to_md_code_block(dict_data: Dict) -> Dict:
        if not dict_data:
            return

        format_dict = "\n"
        for key, value in dict_data.items():
            format_dict += f" - {key}: {value}\n"
        format_dict += ""
        return format_dict
