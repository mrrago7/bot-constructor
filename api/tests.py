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

    def test_bot_list(self):
        response = self.client.get('/api/bots/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['name'],
            'Test Bot'
        )

    def test_bot_create(self):
        response = self.client.post(
            '/api/bots/',
            {
                'name': 'New Bot',
                'description': 'New description',
                'owner': self.user.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'New Bot')

    def test_bot_detail(self):
        response = self.client.get(
            f'/api/bots/{self.bot.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Bot')

    def test_bot_update(self):
        response = self.client.put(
            f'/api/bots/{self.bot.id}/',
            {
                'name': 'Updated Bot',
                'description': 'Updated description',
                'owner': self.user.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated Bot')

    def test_bot_delete(self):
        response = self.client.delete(
            f'/api/bots/{self.bot.id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Bot.objects.filter(id=self.bot.id).exists()
        )

    def test_scenario_list(self):
        response = self.client.get('/api/scenarios/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['name'],
            'Test Scenario'
        )

    def test_scenario_create(self):
        new_bot = Bot.objects.create(
            name='New Bot',
            description='New description',
            owner=self.user
        )

        response = self.client.post(
            '/api/scenarios/',
            {
                'bot': new_bot.id,
                'name': 'New Scenario',
                'description': 'New description',
                'data': {}
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'New Scenario')
    def test_scenario_detail(self):
        response = self.client.get(
            f'/api/scenarios/{self.scenario.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Scenario')

    def test_scenario_update(self):
        response = self.client.put(
            f'/api/scenarios/{self.scenario.id}/',
            {
                'bot': self.bot.id,
                'name': 'Updated Scenario',
                'description': 'Updated description',
                'data': {}
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated Scenario')

    def test_scenario_delete(self):
        response = self.client.delete(
            f'/api/scenarios/{self.scenario.id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Scenario.objects.filter(id=self.scenario.id).exists()
        )

    def test_step_create(self):
        response = self.client.post(
            f'/api/scenarios/{self.scenario.id}/steps/',
            {
                'scenario': self.scenario.id,
                'name': 'Second step',
                'order': 2,
                'prompt': 'Второй вопрос'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Second step')
    def test_step_list(self):
        response = self.client.get(
            f'/api/scenarios/{self.scenario.id}/steps/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_step_update(self):
        response = self.client.put(
            f'/api/scenarios/{self.scenario.id}/steps/{self.step.id}/',
            {
                'scenario': self.scenario.id,
                'name': 'Updated step',
                'order': 1,
                'prompt': 'Обновлённый вопрос'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated step')
    def test_step_delete(self):
        response = self.client.delete(
            f'/api/scenarios/{self.scenario.id}/steps/{self.step.id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Step.objects.filter(id=self.step.id).exists()
        )
