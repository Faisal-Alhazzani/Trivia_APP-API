import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Completed:
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=888')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_for_category_does_not_exist(self):
        res = self.client().get('/categories/777')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    # Delete test will pass the first run, after the first run we need to change question id because the first
    # question has been deleted and doesn't exist which make sense
    def test_delete_question(self):
        resp = self.client().delete('/questions/1')
        data = json.loads(resp.data)

        self.assertEqual(data['success'], True)

    def test_422_for_failed_delete(self):
        resp = self.client().delete('/questions/666')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_question(self):
        new_question = {
            'question': 'tt question',
            'answer': 'tt answer',
            'difficulty': 2,
            'category': 2
        }
        resp = self.client().post('/questions', json=new_question)
        data = json.loads(resp.data)

        self.assertEqual(data['success'], True)

    def test_422_for_failed_add(self):
        new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 22,
            'category': 122
        }
        resp = self.client().post('/questions', json=new_question)
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_question(self):
        resp = self.client().post('/questions/search', json={'searchTerm': 'what'})
        data = json.loads(resp.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_if_search_failed(self):
        resp = self.client().post('/questions/search', json={'searchTerm': ''})
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_per_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_if_questions_per_category_failed(self):
        res = self.client().get('/categories/mm/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()