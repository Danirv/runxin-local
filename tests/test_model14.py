"""Issue #22's model-14 policy; no raw hardware capture was supplied."""
from .helpers import load

models = load("models")
codec = load("runxin.f79d")


def test_model14_accepts_reported_identity_with_scoped_alpha_evidence():
    model = models.controller_model(14)
    assert model.support_level == "alpha"
    assert model.protocol_profile == "f79d"
    assert not model.read_only
    assert model.allowed_write_fields == models.EXISTING_CONTROL_FIELDS
    assert model.hardware_verified_write_fields == (4, 6, 10, 43)
    assert model.pending_write_fields == (7, 34, 47)
    assert "contributor reports" in model.evidence
    assert "F136" in model.model_name
    assert 49 not in model.allowed_write_fields


def test_midnight_scale_is_usable_and_its_confirmation_is_explicit():
    # Synthetic input, not a model-14 capture or a physical 25 L observation.
    data = codec.decode_tlvs({1: (14, 0), 26: (250, 0), 34: (0, 0)})
    assert data["deviceModel"] == 14
    assert data["_raw_resinVolumeBytes"] == (250, 0)
    assert models.resin_volume_litres(data["resinVolume"], 14) == 25.0
    assert not models.model_support_details(14)["resin_volume_scale_confirmed"]
    assert models.model_support_details(12)["resin_volume_scale_confirmed"]
    assert models.resin_volume_litres(250, 12) == 25.0
    assert models.resin_volume_litres(25, 9) == 25
    assert models.resin_volume_litres(240, 1) is None


def test_model12_adds_f105_name_without_changing_entry_title_or_policy():
    model = models.controller_model(12)
    assert model.title == "Euro-Clear Midnight"
    assert "F105" in model.model_name
    assert model.support_level == "alpha"
    assert model.allowed_write_fields == models.EXISTING_CONTROL_FIELDS
