from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from food11.promote import promote


@pytest.mark.parametrize("candidate,decision", [(0.85, "champion"), (0.81, "challenger")])
def test_quality_gate(candidate, decision):
    client = Mock()
    client.get_model_version.return_value = SimpleNamespace(tags={}, run_id="candidate")
    client.get_model_version_by_alias.return_value = SimpleNamespace(tags={}, run_id="champion", version="1")
    client.get_run.side_effect = lambda run: SimpleNamespace(
        data=SimpleNamespace(metrics={"test_accuracy": candidate if run == "candidate" else 0.8}))
    report = promote(client, "2", 1000)
    assert report["decision"] == decision
    assert report["two_se"] == pytest.approx(0.02529822128)
    client.set_registered_model_alias.assert_called_once_with("food11", decision, "2")
    assert client.set_model_version_tag.call_count == len(report)


def test_missing_metric_does_not_promote():
    client = Mock()
    client.get_model_version.return_value = SimpleNamespace(tags={}, run_id="missing")
    client.get_run.return_value = SimpleNamespace(data=SimpleNamespace(metrics={}))
    with pytest.raises(KeyError):
        promote(client, "2", 1000)
    client.set_registered_model_alias.assert_not_called()
