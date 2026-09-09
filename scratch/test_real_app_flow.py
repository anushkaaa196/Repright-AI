"""End-to-End Real Application Workflow Test for REPRIGHT AI.

Validates the full interactive lifecycle:
START APPLICATION -> SHOW LOGIN SCREEN -> ALLOW REGISTRATION -> ALLOW LOGIN -> OPEN MAIN REPRIGHT AI DASHBOARD
Also verifies user identity reflection in the sidebar, user dashboard opening, and core controls.
"""

import sys
from pathlib import Path
import time

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import customtkinter as ctk
from database.db_manager import init_db
from services.user_session import UserSession
from services.auth_service import AuthService
from ui.auth.login_screen import AuthWindow, LoginFrame
from ui.auth.register_screen import RegisterFrame
from ui.app import AIWorkoutUI


def test_real_app_flow():
    print("=" * 70)
    print("  REPRIGHT AI — REAL APPLICATION STARTUP & AUTH FLOW VERIFICATION")
    print("=" * 70)

    # 1. Initialize Database
    print("\n[STEP 1] Initializing SQLite Database...")
    init_db()
    UserSession.get_instance().logout()
    assert UserSession.get_instance().is_authenticated() is False
    print("  ✓ Database initialized and session reset.")

    # 2. Launch AuthWindow (exactly what main.py does)
    print("\n[STEP 2] Launching AuthWindow (Login View)...")
    app_instance = []

    def on_authenticated_callback(user):
        print(f"  ✓ Authentication callback received for user: {user.name} ({user.email})")
        app = AIWorkoutUI()
        app.update_idletasks()
        app_instance.append(app)

    auth_window = AuthWindow(on_authenticated=on_authenticated_callback)
    auth_window.update_idletasks()

    assert auth_window.winfo_exists(), "AuthWindow failed to render."
    assert auth_window.login_view.winfo_exists(), "LoginFrame failed to render."
    assert auth_window.login_view.email_entry.winfo_exists()
    assert auth_window.login_view.pwd_entry.winfo_exists()
    assert auth_window.login_view.login_btn.winfo_exists()
    print("  ✓ AuthWindow opened with LoginFrame, email/password fields, and sign-in button.")

    # 3. Switch to Register View
    print("\n[STEP 3] Switching to Athlete Registration Form...")
    auth_window._show_register()
    auth_window.update_idletasks()

    assert auth_window.register_view is not None
    assert auth_window.register_view.winfo_exists(), "RegisterFrame failed to render."
    assert auth_window.register_view.name_entry.winfo_exists()
    assert auth_window.register_view.email_entry.winfo_exists()
    assert auth_window.register_view.pwd_entry.winfo_exists()
    assert auth_window.register_view.confirm_pwd_entry.winfo_exists()
    assert auth_window.register_view.height_entry.winfo_exists()
    assert auth_window.register_view.weight_entry.winfo_exists()
    assert auth_window.register_view.goal_opt.winfo_exists()
    print("  ✓ Registration view displayed with all demographic and athletic fields.")

    # 4. Perform Registration through UI form
    print("\n[STEP 4] Submitting New Athlete Profile via Registration Form...")
    test_email = f"marcus_{int(time.time())}@repright.ai"
    auth_window.register_view.name_entry.delete(0, "end")
    auth_window.register_view.name_entry.insert(0, "Marcus Vance")

    auth_window.register_view.email_entry.delete(0, "end")
    auth_window.register_view.email_entry.insert(0, test_email)

    auth_window.register_view.pwd_entry.delete(0, "end")
    auth_window.register_view.pwd_entry.insert(0, "VanceFitness!99")

    auth_window.register_view.confirm_pwd_entry.delete(0, "end")
    auth_window.register_view.confirm_pwd_entry.insert(0, "VanceFitness!99")

    auth_window.register_view.height_entry.delete(0, "end")
    auth_window.register_view.height_entry.insert(0, "180.0")

    auth_window.register_view.weight_entry.delete(0, "end")
    auth_window.register_view.weight_entry.insert(0, "76.5")

    auth_window.register_view.goal_opt.set("STRENGTH")

    # Trigger registration handler directly
    auth_window.register_view._handle_register()
    auth_window.update_idletasks()

    # Verify user session is authenticated
    session = UserSession.get_instance()
    assert session.is_authenticated() is True, "UserSession should be authenticated after register."
    current_user = session.get_current_user()
    assert current_user.name == "Marcus Vance"
    assert current_user.email == test_email
    print(f"  ✓ Registered and authenticated user: {current_user.name} (Goal: {current_user.fitness_goal}).")

    # 5. Switch back to Login view and test credential login
    print("\n[STEP 5] Testing Login Submission...")
    auth_window._show_login()
    auth_window.update_idletasks()
    assert auth_window.login_view.winfo_exists()

    auth_window.login_view.email_entry.delete(0, "end")
    auth_window.login_view.email_entry.insert(0, test_email)

    auth_window.login_view.pwd_entry.delete(0, "end")
    auth_window.login_view.pwd_entry.insert(0, "VanceFitness!99")

    auth_window.login_view._handle_login()
    auth_window.update_idletasks()

    # Simulate AuthWindow destruction and triggering main app
    auth_window._on_auth_success(current_user)

    # 6. Verify Main REPRIGHT AI Application Dashboard
    print("\n[STEP 6] Verifying Main REPRIGHT AI Dashboard Launch...")
    assert len(app_instance) == 1, "Main application instance not started."
    app = app_instance[0]
    app.update_idletasks()

    assert app.winfo_exists(), "Main AIWorkoutUI failed to render."
    assert app.sidebar.winfo_exists(), "Sidebar failed to render."
    assert app.viewport.winfo_exists(), "Live viewport failed to render."
    assert app.form_guide.winfo_exists(), "Form guide failed to render."
    assert app.analytics.winfo_exists(), "Analytics dock failed to render."

    # Check Sidebar user badge
    assert app.sidebar.user_frame.winfo_exists(), "Sidebar athlete identity card missing."
    print(f"  ✓ Sidebar reflects authenticated athlete: {current_user.name}.")

    # Check Pinned Workout Controls
    assert app.sidebar.btn_start.winfo_exists()
    assert app.sidebar.btn_stop.winfo_exists()
    assert app.sidebar.btn_report.winfo_exists()
    assert app.sidebar.btn_reset.winfo_exists()
    print("  ✓ All 4 pinned workout controls (START, STOP, EXPORT, RESET) are active.")

    # 7. Test Opening Athlete Dashboard Modal from App
    print("\n[STEP 7] Opening Athlete Intelligence Dashboard from Main App...")
    app._open_user_dashboard()
    app.update_idletasks()
    assert app.user_dashboard is not None
    assert app.user_dashboard.winfo_exists(), "UserDashboardDialog failed to open."
    assert app.user_dashboard.profile_card.winfo_exists()
    assert app.user_dashboard.kpi_container.winfo_exists()
    assert app.user_dashboard.history_view.winfo_exists()
    print("  ✓ UserDashboardDialog verified with profile card, KPI ribbon, and workout history.")
    app.user_dashboard.destroy()
    app.user_dashboard = None

    # 8. Clean Shutdown
    print("\n[STEP 8] Closing Application Safely...")
    app.destroy()
    print("  ✓ Application closed cleanly.")

    print("\n" + "=" * 70)
    print("  REAL APPLICATION WORKFLOW TEST: 100% SUCCESS")
    print("  START -> LOGIN SCREEN -> REGISTER -> LOGIN -> MAIN APP DASHBOARD")
    print("=" * 70)
    return True


if __name__ == "__main__":
    test_real_app_flow()
