from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fpvs_studio.models.condition import ConditionModel
from fpvs_studio.models.experiment import ExperimentModel


def _condition_to_dict(condition: ConditionModel) -> dict[str, Any]:
    return {
        "id": condition.id,
        "label": condition.label,
        "trigger_code_base": condition.trigger_code_base,
        "trigger_code_oddball": condition.trigger_code_oddball,
        "base_image_dir": str(condition.base_image_dir),
        "oddball_image_dir": str(condition.oddball_image_dir),
    }


def _condition_from_dict(data: dict[str, Any]) -> ConditionModel:
    return ConditionModel(
        id=data.get("id", ""),
        label=data.get("label", ""),
        trigger_code_base=data.get("trigger_code_base", 0),
        trigger_code_oddball=data.get("trigger_code_oddball", 0),
        base_image_dir=Path(data.get("base_image_dir", "")),
        oddball_image_dir=Path(data.get("oddball_image_dir", "")),
    )


def experiment_to_dict(experiment: ExperimentModel) -> dict[str, Any]:
    """
    Convert an ExperimentModel into a JSON-serializable dict.
    Paths are converted to strings.
    """

    return {
        "experiment_id": experiment.experiment_id,
        "name": experiment.name,
        "base_rate_hz": experiment.base_rate_hz,
        "oddball_rate_hz": experiment.oddball_rate_hz,
        "image_on_ms": experiment.image_on_ms,
        "blank_ms": experiment.blank_ms,
        "block_duration_seconds": experiment.block_duration_seconds,
        "num_cycles": experiment.num_cycles,
        "randomize_within_cycle": experiment.randomize_within_cycle,
        "rest_enabled": experiment.rest_enabled,
        "rest_default_seconds": experiment.rest_default_seconds,
        "attention_enabled": experiment.attention_enabled,
        "fixation_min_changes": experiment.fixation_min_changes,
        "fixation_max_changes": experiment.fixation_max_changes,
        "instruction_text": experiment.instruction_text,
        "attention_question_text": experiment.attention_question_text,
        "monitor_refresh_hz": experiment.monitor_refresh_hz,
        "conditions": [_condition_to_dict(cond) for cond in experiment.conditions],
    }


def experiment_from_dict(data: dict[str, Any]) -> ExperimentModel:
    """
    Construct an ExperimentModel from a dict (inverse of experiment_to_dict).
    String paths are converted back to Path objects.
    """

    conditions_data = data.get("conditions", [])
    conditions = [_condition_from_dict(item) for item in conditions_data]

    return ExperimentModel(
        experiment_id=data.get("experiment_id", ""),
        name=data.get("name", ""),
        base_rate_hz=data.get("base_rate_hz", 0.0),
        oddball_rate_hz=data.get("oddball_rate_hz", 0.0),
        image_on_ms=data.get("image_on_ms", 0.0),
        blank_ms=data.get("blank_ms", 0.0),
        block_duration_seconds=data.get("block_duration_seconds", 0),
        num_cycles=data.get("num_cycles", 0),
        randomize_within_cycle=data.get("randomize_within_cycle", False),
        rest_enabled=data.get("rest_enabled", False),
        rest_default_seconds=data.get("rest_default_seconds", 0),
        attention_enabled=data.get("attention_enabled", False),
        fixation_min_changes=data.get("fixation_min_changes", 0),
        fixation_max_changes=data.get("fixation_max_changes", 0),
        instruction_text=data.get("instruction_text", ""),
        attention_question_text=data.get("attention_question_text", ""),
        monitor_refresh_hz=data.get("monitor_refresh_hz"),
        conditions=conditions,
    )


def save_experiment(experiment: ExperimentModel, path: Path) -> None:
    """
    Save experiment to a JSON file at the given path.
    """

    data = experiment_to_dict(experiment)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)


def load_experiment(path: Path) -> ExperimentModel:
    """
    Load experiment from a JSON file at the given path.
    Raises FileNotFoundError or json.JSONDecodeError as appropriate.
    """

    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    return experiment_from_dict(data)
