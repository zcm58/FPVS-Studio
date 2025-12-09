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
    instruction text, and runs BLOCK/REST segments with FPVS base/oddball
    semantics.

    Phase 6 scope:
    - Uses base and oddball image directories for each condition.
    - Emits trigger codes for base and oddball onsets and logs events.
    - No fixation color changes or attention question.
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
        oddball_textures_by_condition: dict[str, list[pyglet.image.AbstractImage]] = {}
        allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp"}
        conditions_by_id = {condition.id: condition for condition in experiment.conditions}
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

            oddball_dir = Path(condition.oddball_image_dir)
            if not oddball_dir.exists():
                raise FileNotFoundError(f"Oddball image directory not found: {oddball_dir}")

            oddball_images = [
                path
                for path in oddball_dir.iterdir()
                if path.suffix.lower() in allowed_extensions and path.is_file()
            ]
            if not oddball_images:
                raise ValueError(
                    f"No oddball images found for condition {condition.id} in {oddball_dir}"
                )

            oddball_textures_by_condition[condition.id] = [
                pyglet.image.load(str(path)) for path in sorted(oddball_images)
            ]

        event_rows: list[str] = []

        def log_event(
            event_type: str,
            segment: Optional[RunSegment] = None,
            base_cycle_index: Optional[int] = None,
            trigger_code: Optional[int] = None,
        ) -> None:
            segment_type = segment.segment_type if segment else ""
            condition_id = segment.condition_id if segment else ""
            event_rows.append(
                ",".join(
                    [
                        datetime.now().isoformat(timespec="milliseconds"),
                        event_type,
                        segment_type,
                        condition_id or "",
                        "" if base_cycle_index is None else str(base_cycle_index),
                        "" if trigger_code is None else str(trigger_code),
                    ]
                )
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
        block_base_textures: list[pyglet.image.AbstractImage] = []
        block_oddball_textures: list[pyglet.image.AbstractImage] = []
        base_cycle_frame = 0
        base_cycle_index = 0
        base_texture_index = 0
        oddball_texture_index = 0
        running_state = "instruction"
        current_condition: Optional[str] = None
        current_cycle_texture: Optional[pyglet.image.AbstractImage] = None

        def start_next_segment() -> None:
            nonlocal current_segment_index, block_frame_count, target_block_frames, block_base_textures, block_oddball_textures, running_state, base_cycle_frame, base_cycle_index, base_texture_index, oddball_texture_index, current_condition
            if current_segment_index >= len(run_plan.segments):
                finish_run()
                return

            segment = run_plan.segments[current_segment_index]
            current_segment_index += 1

            if segment.segment_type == "BLOCK" and segment.condition_id:
                condition_id = segment.condition_id
                if condition_id not in base_textures_by_condition or condition_id not in oddball_textures_by_condition:
                    raise ValueError(f"Textures not loaded for condition {condition_id}")

                block_base_textures = base_textures_by_condition[condition_id]
                block_oddball_textures = oddball_textures_by_condition[condition_id]
                block_frame_count = 0
                target_seconds = segment.duration_seconds or experiment.block_duration_seconds
                target_block_frames = int(target_seconds * timing.frames_per_second)
                base_cycle_frame = 0
                base_cycle_index = 0
                base_texture_index = 0
                oddball_texture_index = 0
                current_condition = condition_id
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
            nonlocal block_frame_count, base_cycle_frame, base_cycle_index, current_cycle_texture, base_texture_index, oddball_texture_index, current_texture
            if not block_base_textures or not current_condition:
                return

            if base_cycle_frame == 0:
                is_oddball_cycle = (
                    timing.oddball_every_n_base > 0
                    and base_cycle_index % timing.oddball_every_n_base == timing.oddball_every_n_base - 1
                )
                condition = conditions_by_id[current_condition]
                if is_oddball_cycle:
                    current_cycle_texture = block_oddball_textures[
                        oddball_texture_index % len(block_oddball_textures)
                    ]
                    oddball_texture_index += 1
                    trigger_code = condition.trigger_code_oddball
                    event_type = "oddball_onset"
                else:
                    current_cycle_texture = block_base_textures[
                        base_texture_index % len(block_base_textures)
                    ]
                    base_texture_index += 1
                    trigger_code = condition.trigger_code_base
                    event_type = "base_onset"

                marker.send(trigger_code)
                log_event(
                    event_type,
                    segment=run_plan.segments[current_segment_index - 1],
                    base_cycle_index=base_cycle_index,
                    trigger_code=trigger_code,
                )

            if base_cycle_frame < timing.image_on_frames:
                current_texture = current_cycle_texture
            elif base_cycle_frame < timing.image_on_frames + timing.blank_frames:
                current_texture = None
            else:
                current_texture = None

            base_cycle_frame += 1
            if base_cycle_frame >= timing.frames_per_base_cycle:
                base_cycle_frame = 0
                base_cycle_index += 1

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

        header = "timestamp,event_type,segment_type,condition_id,base_cycle_index,trigger_code\n"
        event_log_path.write_text(header + "\n".join(event_rows))

        summary_lines = [
            "participant_id,experiment_id,attention_enabled,n_fixation_changes,notes",
            f"{participant_id},{experiment.experiment_id},{experiment.attention_enabled},{n_fixation_changes},Phase6_real_presenter_fpvs_base_oddball=yes",
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
