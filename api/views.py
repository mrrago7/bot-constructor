from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Scenario, Step, Bot
from .serializers import ScenarioSerializer, StepSerializer, BotSerializer


class ScenarioViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def get_serializer_class(self):
        if self.action in ['steps', 'step_detail']:
            return StepSerializer
        return ScenarioSerializer

    @action(detail=True, methods=['get', 'post'])
    def steps(self, request, pk=None):
        scenario = self.get_object()
        if request.method == 'POST':
            serializer = StepSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(scenario=scenario)
            return Response(serializer.data, status=201)

        steps = Step.objects.filter(scenario=scenario)
        serializer = StepSerializer(steps, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'delete'], url_path='steps/(?P<step_id>[^/.]+)')
    def step_detail(self, request, pk=None, step_id=None):
        scenario = self.get_object()
        step = get_object_or_404(Step, pk=step_id, scenario=scenario)
        if request.method == 'GET':
            serializer = StepSerializer(step)
            return Response(serializer.data)

        if request.method == 'DELETE':
            step.delete()
            return Response(status=204)

        serializer = StepSerializer(step, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(scenario=scenario)
        return Response(serializer.data)



class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer


class BotViewSet(viewsets.ModelViewSet):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
