from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import Bot, Scenario, Step
from openai import OpenAIError

class BotChatTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        self.bot = Bot.objects.create(
            name='Test Bot',
            description='Test description',
            owner=self.user
        )

        self.scenario = Scenario.objects.create(
            bot=self.bot,
            name='Test Scenario',
            description='Test description',
            data={}
        )

        self.step = Step.objects.create(
            scenario=self.scenario,
            name='First step',
            order=1,
            prompt='Ты полезный помощник.'
        )

    @patch('api.views.get_gpt_response')
    def test_chat_success(self, mock_gpt):
        mock_gpt.return_value = 'Привет! Я тестовый бот.'

        response = self.client.post(
            f'/api/bots/{self.bot.id}/chat/',
            {'message': 'Привет!'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['answer'],
            'Привет! Я тестовый бот.'
        )
        mock_gpt.assert_called_once()

    def test_chat_without_message(self):
        response = self.client.post(
            f'/api/bots/{self.bot.id}/chat/',
            {},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['error'],
            'Поле message обязательно.'
        )

    def test_chat_without_scenario(self):
        self.scenario.delete()

        response = self.client.post(
            f'/api/bots/{self.bot.id}/chat/',
            {'message': 'Привет!'},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['error'],
            'У бота нет сценария.'
        )



    @patch('api.views.get_gpt_response')
    def test_chat_gpt_error(self, mock_gpt):
        mock_gpt.side_effect = OpenAIError('API error')

        response = self.client.post(
            f'/api/bots/{self.bot.id}/chat/',
            {'message': 'Привет!'},
            format='json'
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.data['error'],
            'Не удалось получить ответ от GPT.'
        )

    @patch('api.views.get_gpt_response')
    def test_chat_step_transition(self, mock_gpt):
        mock_gpt.return_value = 'Ответ бота'

        second_step = Step.objects.create(
            scenario=self.scenario,
            name='Second step',
            order=2,
            prompt='Второй вопрос'
        )

        self.step.next_step = second_step
        self.step.save()

        # Первый запрос — начинаем диалог
        response = self.client.post(
            f'/api/bots/{self.bot.id}/chat/',
            {'message': 'Привет!'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        conversation_id = response.data['conversation_id']

        self.assertEqual(
            response.data['next_step'],
            second_step.id
        )

        # Второй запрос — продолжаем диалог
        response = self.client.post(
            f'/api/bots/{self.bot.id}/chat/',
            {
                'message': 'Продолжаем',
                'conversation_id': conversation_id
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['next_step'])

        self.assertEqual(mock_gpt.call_count, 2)
        self.assertIn('Второй вопрос', mock_gpt.call_args[0][0])