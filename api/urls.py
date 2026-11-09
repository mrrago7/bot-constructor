from rest_framework.routers import DefaultRouter
from .views import BotViewSet, ScenarioViewSet, StepViewSet

router = DefaultRouter()
router.register(r'bots', BotViewSet)
router.register(r'scenarios', ScenarioViewSet)
router.register(r'steps', StepViewSet)
urlpatterns = router.urls