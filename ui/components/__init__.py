"""UI components package for REPRIGHT AI."""

from .sidebar import SidebarFrame
from .viewport import ViewportFrame
from .form_guide import FormGuideFrame
from .posture_correction import PostureCorrectionCard
from .body_focus import BodyFocusCard
from .smart_coach import SmartCoachCard
from .analytics import LiveAnalyticsFrame
from .exercise_library import ExerciseLibraryDialog
from .readiness_check import ReadinessCheckCard
from .session_summary import SessionSummaryDialog
from .rep_timeline import RepTimelineFrame
from .performance_breakdown import PerformanceBreakdownFrame
from .personalized_plan import PersonalizedPlanCard, PersonalizedPlanDialog
from .session_goal import SessionGoalCard
from .form_comparison import FormComparisonCard
from .progress_dashboard import ProgressDashboardDialog
from .movement_phase import MovementPhaseCard
from .movement_heatmap import MovementHeatmapFrame
from .movement_intelligence import MovementIntelligenceCard, MovementIntelligenceDialog
from .demo_mode import SIHDemoWindow
from .collapsible_card import CollapsibleCard
from .consistency_view import ConsistencyView
from .trend_view import TrendView
from .analytics_navigation import AnalyticsNavBar, QuickAnalyticsMenu
from .analytics_hub import AnalyticsHubDialog
from .user_dashboard import UserDashboardDialog
from .user_profile import UserProfileDialog
from .workout_history import WorkoutHistoryView
from .nutrition_profile import NutritionProfileDialog
from .nutrition_dashboard import NutritionDashboardDialog
from .gym_locator import GymLocatorDialog


__all__ = [
    "SidebarFrame",
    "ViewportFrame",
    "FormGuideFrame",
    "PostureCorrectionCard",
    "BodyFocusCard",
    "SmartCoachCard",
    "LiveAnalyticsFrame",
    "ExerciseLibraryDialog",
    "ReadinessCheckCard",
    "SessionSummaryDialog",
    "RepTimelineFrame",
    "PerformanceBreakdownFrame",
    "PersonalizedPlanCard",
    "PersonalizedPlanDialog",
    "SessionGoalCard",
    "FormComparisonCard",
    "ProgressDashboardDialog",
    "MovementPhaseCard",
    "MovementHeatmapFrame",
    "MovementIntelligenceCard",
    "MovementIntelligenceDialog",
    "SIHDemoWindow",
    "CollapsibleCard",
    "ConsistencyView",
    "TrendView",
    "AnalyticsNavBar",
    "QuickAnalyticsMenu",
    "AnalyticsHubDialog",
    "UserDashboardDialog",
    "UserProfileDialog",
    "WorkoutHistoryView",
    "NutritionProfileDialog",
    "NutritionDashboardDialog",
    "GymLocatorDialog"
]

