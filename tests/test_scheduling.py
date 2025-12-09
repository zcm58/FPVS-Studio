import random
import unittest

from fpvs_studio.controllers.scheduling import build_run_plan
from fpvs_studio.models import ConditionModel, ExperimentModel


class BuildRunPlanRestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.condition_a = ConditionModel(
            id="A",
            label="Condition A",
            trigger_code_base=1,
            trigger_code_oddball=2,
            base_image_dir="/tmp/base_a",
            oddball_image_dir="/tmp/odd_a",
        )
        self.condition_b = ConditionModel(
            id="B",
            label="Condition B",
            trigger_code_base=3,
            trigger_code_oddball=4,
            base_image_dir="/tmp/base_b",
            oddball_image_dir="/tmp/odd_b",
        )

    def _base_experiment(self) -> ExperimentModel:
        return ExperimentModel(
            experiment_id="exp",
            name="Example",
            base_rate_hz=6.0,
            oddball_rate_hz=1.2,
            image_on_ms=166.0,
            blank_ms=0.0,
            block_duration_seconds=60,
            num_cycles=2,
            randomize_within_cycle=False,
            rest_enabled=True,
            rest_default_seconds=10,
            attention_enabled=False,
            fixation_min_changes=0,
            fixation_max_changes=0,
            instruction_text="",
            attention_question_text="",
            conditions=[self.condition_a, self.condition_b],
        )

    def test_rest_inserted_once_between_cycles(self) -> None:
        experiment = self._base_experiment()
        plan = build_run_plan(experiment, random.Random(123))

        segment_types = [segment.segment_type for segment in plan]
        self.assertEqual(segment_types, ["BLOCK", "BLOCK", "REST", "BLOCK", "BLOCK"])

        rest_segments = [segment for segment in plan if segment.segment_type == "REST"]
        self.assertEqual(len(rest_segments), 1)
        rest = rest_segments[0]
        self.assertEqual(rest.after_cycle_index, 0)
        self.assertEqual(rest.after_block_index, 1)
        self.assertEqual(rest.duration_seconds, experiment.rest_default_seconds)


if __name__ == "__main__":
    unittest.main()
