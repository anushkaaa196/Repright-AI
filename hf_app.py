"""Browser entry point for deploying TruForm AI on Hugging Face Spaces.

The desktop application uses Tkinter and a server-side camera, which are not
available in a browser Space. This entry point receives webcam frames from
Gradio and reuses the project's YOLO pose model and geometry helpers.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import cv2
import gradio as gr
import numpy as np
from ultralytics import YOLO

from config import EXERCISE_CONFIGS, POSE_MODEL_IMGSZ, PROFILE_CONF_THRESHOLD
from core.geometry import extract_exercise_data


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "yolov8n-pose.pt"
MODEL = YOLO(str(MODEL_PATH))

SKELETON = (
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
    (5, 11), (6, 12), (11, 12), (11, 13), (13, 15),
    (12, 14), (14, 16),
)


def _new_state() -> Dict[str, Any]:
    return {"phase": "ready", "reps": 0, "warnings": 0, "started": False}


def _draw_pose(frame: np.ndarray, keypoints: np.ndarray, confidence: np.ndarray) -> None:
    """Draw the detected skeleton without depending on the desktop UI."""
    for start, end in SKELETON:
        if confidence[start] >= PROFILE_CONF_THRESHOLD and confidence[end] >= PROFILE_CONF_THRESHOLD:
            p1 = tuple(np.int32(keypoints[start]))
            p2 = tuple(np.int32(keypoints[end]))
            cv2.line(frame, p1, p2, (0, 220, 190), 2)
    for point, score in zip(keypoints, confidence):
        if score >= PROFILE_CONF_THRESHOLD:
            cv2.circle(frame, tuple(np.int32(point)), 4, (255, 255, 255), -1)


def _feedback(exercise: str, data: Dict[str, Any], state: Dict[str, Any]) -> str:
    cfg = EXERCISE_CONFIGS[exercise]
    angle = data.get("angle")
    if angle is None:
        return "Move into view so the required joints are visible."

    if exercise == "BICEP_CURL":
        angles = [data.get("l_angle"), data.get("r_angle")]
        angles = [value for value in angles if value is not None]
        if any(value <= cfg["target_angle"] for value in angles):
            state["phase"] = "peak"
            return "Peak contraction detected. Lower with control."
        if any(value < cfg["down_thresh"] for value in angles):
            state["phase"] = "curling"
            return "Curling up. Keep elbows close to your ribs."
        state["phase"] = "ready"
        return "Ready. Begin the repetition from full extension."

    if angle <= cfg["target_angle"]:
        state["phase"] = "depth"
        return f"Target {exercise.lower()} depth reached. Drive back up."
    if angle < cfg["down_thresh"]:
        state["phase"] = "descending"
        return "Movement detected. Continue to the target range."
    state["phase"] = "ready"
    return "Ready. Start from your standing position."


def analyze_frame(
    frame: Optional[np.ndarray],
    exercise: str,
    state: Optional[Dict[str, Any]],
) -> Tuple[Optional[np.ndarray], str, Dict[str, Any]]:
    if frame is None:
        return None, "Waiting for a webcam frame.", state or _new_state()

    state = state or _new_state()
    previous_phase = state["phase"]
    image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    result = MODEL(image, imgsz=POSE_MODEL_IMGSZ, verbose=False)[0]

    if result.keypoints is None or len(result.keypoints.xy) == 0:
        return frame, "### No person detected\nMove farther into the camera view.", state

    keypoints = result.keypoints.xy[0].cpu().numpy()
    confidence = (
        result.keypoints.conf[0].cpu().numpy()
        if result.keypoints.conf is not None
        else np.ones(len(keypoints))
    )
    _draw_pose(image, keypoints, confidence)

    data = extract_exercise_data(
        exercise,
        keypoints,
        confidence,
        conf_threshold=PROFILE_CONF_THRESHOLD,
    )
    message = _feedback(exercise, data, state) if data["valid"] else (
        data.get("missing_feedback") or "Keep your full body in the camera view."
    )
    if previous_phase in {"depth", "peak"} and state["phase"] == "ready":
        state["reps"] += 1
    angle = data.get("angle")
    angle_text = f"{angle:.1f} deg" if angle is not None else "--"
    cv2.putText(image, message[:80], (16, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 200), 2)

    stats = (
        f"### {exercise.replace('_', ' ').title()}\n"
        f"**Joint angle:** {angle_text}  \n"
        f"**Detected reps:** {state['reps']}  \n"
        f"**Phase:** {state['phase'].title()}  \n\n{message}"
    )
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), stats, state


def reset_state() -> Dict[str, Any]:
    return _new_state()


with gr.Blocks(title="TruForm AI") as demo:
    gr.Markdown("# TruForm AI\nBrowser-based exercise form analysis")
    with gr.Row():
        with gr.Column(scale=2):
            camera = gr.Image(
                sources=["webcam"],
                type="numpy",
                label="Webcam",
                streaming=True,
            )
        with gr.Column():
            exercise = gr.Dropdown(
                choices=list(EXERCISE_CONFIGS),
                value="SQUAT",
                label="Exercise",
            )
            metrics = gr.Markdown("Start your camera to begin.")
            reset = gr.Button("Reset session")
    session = gr.State(_new_state())
    camera.stream(analyze_frame, [camera, exercise, session], [camera, metrics, session], stream_every=0.15)
    reset.click(reset_state, outputs=session)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)