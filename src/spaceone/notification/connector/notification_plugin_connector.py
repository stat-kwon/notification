import logging

from spaceone.core.connector import BaseConnector
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core.auth.jwt.jwt_util import JWTUtil

__all__ = ["NotificationPluginConnector"]
_LOGGER = logging.getLogger(__name__)


class NotificationPluginConnector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        token = self.transaction.get_meta("token")
        self.token_type = JWTUtil.get_value_from_token(token, "typ")
        self.noti_plugin_connector = None

    def initialize(self, endpoint: str):
        static_endpoint = self.config.get("endpoint")

        if static_endpoint:
            endpoint = static_endpoint

        self.noti_plugin_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint
        )

    def init(self, options, domain_id=None):
        if self.token_type == "SYSTEM_TOKEN":
            return self.noti_plugin_connector.dispatch(
                "Protocol.init", {"options": options}, x_domain_id=domain_id
            )
        else:
            return self.noti_plugin_connector.dispatch(
                "Protocol.init", {"options": options}
            )

    def verify(self, options, secret_data):
        params = {"options": options, "secret_data": secret_data}

        self.noti_plugin_connector.dispatch("Protocol.verify", params)

    def dispatch_notification(
            self, secret_data: dict, channel_data, notification_type, message, options={}, domain_id=None
    ):
        params = {
            "secret_data": secret_data,
            "channel_data": channel_data,
            "notification_type": notification_type,
            "message": message,
            "options": options,
        }

        if self.token_type == "SYSTEM_TOKEN":
            return self.noti_plugin_connector.dispatch(
                "Notification.dispatch", params, x_domain_id=domain_id
            )
        else:
            return self.noti_plugin_connector.dispatch("Notification.dispatch", params)
