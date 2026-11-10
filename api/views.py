from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Scenario, Step, Bot, Conversation
from .serializers import ScenarioSerializer, StepSerializer, BotSerializer
from .services import get_gpt_response
from openai import OpenAIError


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

    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        bot = self.get_object()

        message = request.data.get('message')
        if not message:
            return Response(
                {'error': 'Поле message обязательно.'},
                status=400
            )

        conversation_id = request.data.get('conversation_id')

        if conversation_id:
            conversation = get_object_or_404(
                Conversation,
                pk=conversation_id,
                bot=bot
            )
        else:
            try:
                scenario = bot.scenario
            except Scenario.DoesNotExist:
                return Response(
                    {'error': 'У бота нет сценария.'},
                    status=400
                )

            first_step = scenario.step_set.order_by('order').first()

            if first_step is None:
                return Response(
                    {'error': 'В сценарии нет шагов.'},
                    status=400
                )

            conversation = Conversation.objects.create(
                bot=bot,
                current_step=first_step
            )

        step = conversation.current_step

        if step is None:
            return Response(
                {'error': 'В диалоге отсутствует текущий шаг.'},
                status=400
            )

        prompt = f"{step.prompt}\n\nСообщение пользователя: {message}"

        try:
            answer = get_gpt_response(prompt)
        except OpenAIError:
            return Response(
                {'error': 'Не удалось получить ответ от GPT.'},
                status=503
            )

        conversation.current_step = step.next_step
        conversation.save()

        return Response({
            'answer': answer,
            'conversation_id': conversation.id,
            'next_step': conversation.current_step.id
            if conversation.current_step else None
        })
