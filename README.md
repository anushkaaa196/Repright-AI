# 🏋️ REPRIGHT AI

## AI-Powered Real-Time Exercise Form & Biomechanics Analysis Platform

**REPRIGHT AI** is an AI-powered real-time exercise form analysis system designed to help users perform exercises with correct posture and movement techniques.

The system uses **Computer Vision, Human Pose Estimation, and Artificial Intelligence** to analyze body movements in real time and identify potential posture and form-related issues during exercise.

---

## 🚀 Problem Statement

Incorrect exercise posture and movement can lead to:

* ❌ Muscle strain and injuries
* ❌ Joint and spine-related problems
* ❌ Reduced exercise effectiveness
* ❌ Long-term physical damage

Professional trainers can continuously monitor exercise form, but such guidance may not always be accessible or affordable.

**REPRIGHT AI addresses this challenge by providing an intelligent and accessible system for automated exercise form analysis.**

---

## 💡 Solution

REPRIGHT AI uses an AI-driven approach to analyze human body movements through a camera.

The system:

1. 📷 Captures the user's exercise movement.
2. 🧍 Detects human body posture and keypoints.
3. 🧠 Analyzes body movement and biomechanics.
4. 📐 Evaluates exercise form and posture.
5. ⚠️ Identifies incorrect movement patterns.
6. 💬 Provides real-time feedback to help improve exercise performance.

---

## ✨ Key Features

* 🎥 **Real-Time Exercise Analysis**
* 🧍 **Human Pose Detection**
* 🤖 **AI-Powered Biomechanics Analysis**
* 📐 **Body Keypoint Detection**
* ⚠️ **Incorrect Posture Detection**
* 🏋️ **Exercise Form Evaluation**
* 💬 **Real-Time Feedback**
* 🖥️ **Interactive Desktop User Interface**
* 🧠 **YOLOv8 Pose Estimation Integration**
* 📍 **Nearby Gym & Fitness Center Locator (Device Geolocation + Google Maps Integration)**

---

## 🧠 Technology Stack

| Technology       | Purpose                             |
| ---------------- | ----------------------------------- |
| 🐍 Python        | Core Programming Language           |
| 🤖 YOLOv8 Pose   | Human Pose Detection                |
| 🔥 PyTorch       | Deep Learning Framework             |
| 👁️ OpenCV       | Computer Vision & Camera Processing |
| 🎨 CustomTkinter | Modern Desktop User Interface       |
| 🧮 NumPy         | Numerical & Mathematical Processing |
| 🖼️ Pillow       | Image Processing                    |
| ⚡ Ultralytics    | YOLO AI Model Integration           |

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │    User / Camera    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Video Capture    │
                    │      OpenCV        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Human Pose Detection│
                    │     YOLOv8 Pose     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Body Keypoints    │
                    │      Analysis       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Biomechanics Engine │
                    │  Posture Analysis   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Exercise Form Check │
                    │ & Error Detection   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Real-Time Feedback │
                    │     User Interface  │
                    └─────────────────────┘
```

---

# 📁 Project Structure

```text
RepRight-AI/
│
├── assets/
│   └── exercises/          # Exercise-related assets
│
├── backend/                # Backend processing components
│
├── core/                   # Core AI and biomechanics logic
│
├── scratch/                # Experimental/testing components
│
├── ui/                     # User interface components
│
├── app.py                  # Application-related module
├── app_ui.py               # User interface implementation
├── config.py               # Project configuration
├── main.py                 # Main application entry point
│
├── requirements.txt        # Required Python dependencies
│
└── yolov8n-pose.pt         # YOLOv8 Pose Estimation Model
```

---

# ⚙️ Installation Guide

## 1️⃣ Clone the Repository

Open Terminal, Command Prompt, or VS Code Terminal and run:

```bash
git clone https://github.com/anushkaaa196/TruForm-AI.git
```

Move into the project directory:

```bash
cd TruForm-AI
```

---

## 2️⃣ Create a Virtual Environment (Recommended)

### Windows

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
```

Activate the environment:

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Required Dependencies

Run:

```bash
pip install -r requirements.txt
```

The project uses the following major dependencies:

* Ultralytics
* CustomTkinter
* OpenCV
* Pillow
* NumPy
* PyTorch
* Torchvision

---

# ▶️ Running REPRIGHT AI

After installing all dependencies, run:

```bash
python main.py
```

The application will launch the **REPRIGHT AI user interface**.

Make sure your computer has a working **webcam/camera**, as the system performs real-time exercise and posture analysis.

---

# 🔄 How REPRIGHT AI Works

```text
START
  │
  ▼
Launch REPRIGHT AI
  │
  ▼
Select / Start Exercise Analysis
  │
  ▼
Camera Captures User Movement
  │
  ▼
YOLOv8 Detects Human Pose
  │
  ▼
Body Keypoints Are Extracted
  │
  ▼
Biomechanics & Movement Analysis
  │
  ▼
Exercise Form Evaluation
  │
  ├───────────────┐
  │               │
Correct Form    Incorrect Form
  │               │
  ▼               ▼
Positive       Error Detection
Feedback       & Correction Feedback
  │               │
  └───────┬───────┘
          │
          ▼
     Continue Analysis
```

---

# 🎯 Applications

REPRIGHT AI can potentially be used in:

* 🏋️ Fitness Training
* 🏠 Home Workouts
* 🏥 Physiotherapy Assistance
* 🧑‍⚕️ Rehabilitation Support
* 🏫 Sports Training
* 🤸 Exercise Education
* 💪 Personal Fitness Monitoring

---

# 🔮 Future Enhancements

Future versions of REPRIGHT AI may include:

* 📊 Exercise performance scoring
* 🔊 Voice-based real-time feedback
* 📈 Progress tracking and analytics
* 🏋️ Support for additional exercises
* 📱 Mobile application integration
* ☁️ Cloud-based user profiles
* 🤖 Personalized AI workout recommendations
* 🧑‍⚕️ Advanced rehabilitation monitoring
* 📹 Exercise session recording and reports

---

# 🏆 Innovation

REPRIGHT AI combines:

> **Artificial Intelligence + Computer Vision + Human Pose Estimation + Biomechanics Analysis**

to create an intelligent system capable of automatically analyzing exercise movements and providing feedback on posture and form.

The goal is to make exercise guidance more **accessible, intelligent, and scalable**.

---

# 🛠️ Requirements

* Python **3.10 or later recommended**
* Webcam / Camera
* Internet connection for initial dependency installation
* Windows, macOS, or Linux

---

# ⚠️ Important Note

REPRIGHT AI is designed as an **AI-assisted exercise form analysis system**.

It should not be considered a replacement for professional medical advice, diagnosis, physiotherapy, or certified personal training.

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Submit a Pull Request.

---

# 👩‍💻 Developed For

## Smart India Hackathon (SIH)

**REPRIGHT AI — Intelligent Exercise Form & Biomechanics Analysis Platform**

---

# 📬 Repository

🔗 **GitHub:**
https://github.com/anushkaaa196/TruForm-AI

---

## ⭐ If you find this project interesting, consider giving the repository a star!

**REPRIGHT AI — Train Smarter. Move Better. Stay Safe. 🏋️🤖**
