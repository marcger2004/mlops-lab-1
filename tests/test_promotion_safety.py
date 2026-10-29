from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from food11.promote import promote


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -0.1, 1.1])
def test_invalid_accuracy_never_changes_alias(invalid):
    client = Mock()
    client.get_model_version.return_value = SimpleNamespace(tags={}, run_id="candidate")
    client.get_model_version_by_alias.return_value = SimpleNamespace(tags={}, run_id="champion", version="1")
    client.get_run.return_value = SimpleNamespace(data=SimpleNamespace(metrics={"test_accuracy": invalid}))
    with pytest.raises(ValueError):
        promote(client, "2", 1096)
    client.set_registered_model_alias.assert_not_called()
    client.set_model_version_tag.assert_not_called()
