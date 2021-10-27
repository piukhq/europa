from unittest import mock
from django.conf import settings
from django.test import TestCase
from config_service.reporting import teams_notify

settings.TEAMS_WEBHOOK = "http://localhost"


class TestReporting(TestCase):
    @mock.patch("config_service.reporting.requests.post")
    def test_teams_notify_called(self, mock_req):
        teams_notify("test", "test", "test")
        mock_req.assert_called()
