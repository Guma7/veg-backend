from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Recipe, Rating

class RecipeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            recipe_class='ENTRADA',
            style='GOURMET',
            genre='ENTRADA',
            ingredients='Test ingredients',
            instructions='Test instructions',
            author=self.user
        )

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.title, 'Test Recipe')
        self.assertEqual(self.recipe.author, self.user)

    def test_recipe_rating(self):
        rating = Rating.objects.create(
            recipe=self.recipe,
            user=self.user,
            score=8
        )
        self.assertEqual(self.recipe.average_rating, 8)

    def test_recipe_search(self):
        response = self.client.get(reverse('search_recipes'), {'q': 'salada'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')

    def test_recipe_filtering(self):
        response = self.client.get(
            reverse('search_recipes'), 
            {'recipe_class': 'ENTRADA', 'style': 'GOURMET'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')

    # Teste de sugestão de tags removido conforme as instruções do documento

    def test_recipe_validation(self):
        # Teste para tempo de preparo inválido
        data = {
            'title': 'Test'
            # outros campos obrigatórios
        }
        response = self.client.post(reverse('recipe-list'), data)
        self.assertEqual(response.status_code, 400)
