from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pyglet

from fpvs_studio.controllers.scheduling import RunPlan, RunSegment
from fpvs_studio.engine.presenter_base import Presenter, RunResult
from fpvs_studio.markers.base import MarkerBackend
from fpvs_studio.models.experiment import ExperimentModel
from fpvs_studio.models.exceptions import TimingValidationError
from fpvs_studio.models.timing import TimingDerived


class RealPresenter(Presenter):
    """
    Real presenter that opens a full-screen pyglet window, displays the
    instruction text, and runs BLOCK/REST segments using base images only.

    Phase 5 scope:
    - Uses only base_image_dir from each condition (no oddball logic yet).
    - No fixation color changes or attention question.
    - Writes simple CSV logs, similar in spirit to DummyPresenter.
    """

    def __init__(self, base_output_dir: Path, monitor_index: int = 0) -> None:
        self._base_output_dir = base_output_dir
        self._monitor_index = monitor_index

    def run_experiment(
        self,
        experiment: ExperimentModel,
        participant_id: str,
        run_plan: RunPlan,
        n_fixation_changes: int,
        marker: MarkerBackend,
    ) -> RunResult:
        self._base_output_dir.mkdir(parents=True, exist_ok=True)

        if experiment.monitor_refresh_hz is None:
            raise TimingValidationError(
                "Monitor refresh rate must be set for RealPresenter.",
                base_rate_hz=experiment.base_rate_hz,
                oddball_rate_hz=experiment.oddball_rate_hz,
                monitor_refresh_hz=experiment.monitor_refresh_hz,
            )

        timing: TimingDerived = experiment.derive_timing(experiment.monitor_refresh_hz)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"{experiment.experiment_id}_{participant_id}_{timestamp}"
        event_log_path = self._base_output_dir / f"{prefix}_events.csv"
        summary_path = self._base_output_dir / f"{prefix}_summary.csv"

        base_textures_by_condition: dict[str, list[pyglet.image.AbstractImage]] = {}
        allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp"}
        for condition in experiment.conditions:
            base_dir = Path(condition.base_image_dir)
            if not base_dir.exists():
                raise FileNotFoundError(f"Base image directory not found: {base_dir}")

            images = [
                path
                for path in base_dir.iterdir()
                if path.suffix.lower() in allowed_extensions and path.is_file()
            ]
            if not images:
                raise ValueError(f"No base images found for condition {condition.id} in {base_dir}")

            textures = [pyglet.image.load(str(path)) for path in sorted(images)]
            base_textures_by_condition[condition.id] = textures

        event_rows: list[str] = []

        def log_event(event_type: str, segment: Optional[RunSegment] = None) -> None:
            segment_type = segment.segment_type if segment else ""
            condition_id = segment.condition_id if segment else ""
            event_rows.append(
                f"{datetime.now().isoformat()},{event_type},{segment_type},{condition_id or ''}"
            )

        aborted = False
        abort_reason: Optional[str] = None

        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screens = display.get_screens()
        screen_index = min(self._monitor_index, len(screens) - 1)
        screen = screens[screen_index]
        window = pyglet.window.Window(fullscreen=True, screen=screen)

        instruction_label = pyglet.text.Label(
            experiment.instruction_text,
            font_size=24,
            x=window.width // 2,
            y=window.height // 2,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=int(window.width * 0.8),
        )
        rest_label = pyglet.text.Label(
            "Rest — next block starts soon.",
            font_size=32,
            x=window.width // 2,
            y=window.height // 2,
            anchor_x="center",
            anchor_y="center",
        )
        complete_label = pyglet.text.Label(
            "Experiment Complete", font_size=32, x=window.width // 2, y=window.height // 2, anchor_x="center", anchor_y="center"
        )

        current_segment_index = 0
        current_texture: Optional[pyglet.image.AbstractImage] = None
        block_frame_count = 0
        target_block_frames = 0
        block_textures: list[pyglet.image.AbstractImage] = []
        block_texture_index = 0
        running_state = "instruction"

        def start_next_segment() -> None:
            nonlocal current_segment_index, block_frame_count, target_block_frames, block_textures, block_texture_index, running_state
            if current_segment_index >= len(run_plan.segments):
                finish_run()
                return

            segment = run_plan.segments[current_segment_index]
            current_segment_index += 1

            if segment.segment_type == "BLOCK" and segment.condition_id:
                block_textures = base_textures_by_condition[segment.condition_id]
                block_texture_index = 0
                block_frame_count = 0
                target_block_frames = int(experiment.block_duration_seconds * timing.frames_per_second)
                running_state = "block"
                marker.send(0)
                log_event("block_start", segment)
                pyglet.clock.schedule_interval(block_tick, 1 / timing.frames_per_second)
            elif segment.segment_type == "REST" and segment.duration_seconds is not None:
                running_state = "rest"
                log_event("rest_start", segment)
                pyglet.clock.schedule_once(lambda dt: end_rest(segment), segment.duration_seconds)
            else:
                log_event("segment_skipped", segment)
                start_next_segment()

        def block_tick(dt: float) -> None:
            nonlocal block_frame_count, block_texture_index, current_texture
            if not block_textures:
                return
            current_texture = block_textures[block_texture_index % len(block_textures)]
            block_texture_index += 1
            block_frame_count += 1
            if block_frame_count >= target_block_frames:
                end_block()

        def end_block() -> None:
            nonlocal running_state
            pyglet.clock.unschedule(block_tick)
            running_state = "transition"
            segment = run_plan.segments[current_segment_index - 1]
            log_event("block_end", segment)
            marker.send(0)
            start_next_segment()

        def end_rest(segment: RunSegment) -> None:
            log_event("rest_end", segment)
            start_next_segment()

        def finish_run() -> None:
            nonlocal running_state
            running_state = "complete"
            log_event("run_complete")
            pyglet.clock.schedule_once(lambda dt: pyglet.app.exit(), 0.5)

        @window.event
        def on_draw() -> None:
            window.clear()
            if running_state == "instruction":
                instruction_label.draw()
            elif running_state == "block":
                if current_texture:
                    current_texture.blit(0, 0, width=window.width, height=window.height)
            elif running_state == "rest":
                rest_label.draw()
            elif running_state == "complete":
                complete_label.draw()

        @window.event
        def on_key_press(symbol, modifiers):  # type: ignore[override]
            if running_state == "instruction":
                running_state_transition_from_instruction()

        def running_state_transition_from_instruction() -> None:
            nonlocal running_state
            log_event("instruction_end")
            running_state = "transition"
            start_next_segment()

        try:
            log_event("instruction_start")
            pyglet.app.run()
        except Exception as exc:  # pragma: no cover - runtime safeguard
            aborted = True
            abort_reason = str(exc)
        finally:
            if not window.has_exit:
                window.close()

        if aborted:
            log_event("aborted")

        header = "timestamp,event_type,segment_type,condition_id\n"
        event_log_path.write_text(header + "\n".join(event_rows))

        summary_lines = [
            "participant_id,experiment_id,attention_enabled,n_fixation_changes,notes",
            f"{participant_id},{experiment.experiment_id},{experiment.attention_enabled},{n_fixation_changes},Phase5_real_presenter_base_only=yes",
        ]
        summary_path.write_text("\n".join(summary_lines))

        return RunResult(
            participant_id=participant_id,
            experiment_id=experiment.experiment_id,
            aborted=aborted,
            abort_reason=abort_reason,
            attention_enabled=experiment.attention_enabled,
            n_fixation_changes=n_fixation_changes,
            true_change_count=0,
            reported_change_count=None,
            confirmed=False,
            correct=None,
            absolute_error=None,
            event_log_path=event_log_path,
            run_summary_path=summary_path,
        )
