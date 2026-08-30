"""Tests for safety-critical alarm commands."""

from unittest import mock

import pytest

from ultrasync import AlarmScene, UltraSync
from ultrasync.common import NX595EVendor, XGZWPanelFunction


@pytest.mark.parametrize(
    "vendor",
    (NX595EVendor.ZEROWIRE, NX595EVendor.XGEN, NX595EVendor.XGEN8),
)
@pytest.mark.parametrize(
    "scene",
    (AlarmScene.FIRE, AlarmScene.MEDICAL, AlarmScene.PANIC),
)
def test_emergency_scene_never_falls_back_to_disarm(vendor, scene):
    """Unsupported emergency scenes must not send any panel command."""
    panel = UltraSync()
    panel.session_id = "session"
    panel.vendor = vendor
    panel.areas = {0: {"name": "Area 1"}}
    panel._UltraSync__get = mock.Mock(return_value={"ok": True})

    assert panel.set_alarm(areas=1, state=scene) is False
    panel._UltraSync__get.assert_not_called()


@pytest.mark.parametrize(
    ("scene", "function"),
    (
        (AlarmScene.STAY, XGZWPanelFunction.AREA_STAY),
        (AlarmScene.AWAY, XGZWPanelFunction.AREA_AWAY),
        (AlarmScene.DISARMED, XGZWPanelFunction.AREA_DISARM),
    ),
)
def test_xgen8_supported_scene_uses_explicit_function(scene, function):
    """Supported scenes use their matching panel function."""
    panel = UltraSync()
    panel.session_id = "session"
    panel.vendor = NX595EVendor.XGEN8
    panel.areas = {0: {"name": "Area 1"}}
    panel._UltraSync__get = mock.Mock(return_value={"ok": True})

    assert panel.set_alarm(areas=1, state=scene) is True
    panel._UltraSync__get.assert_called_once()
    assert panel._UltraSync__get.call_args.kwargs["payload"]["fnum"] == function
