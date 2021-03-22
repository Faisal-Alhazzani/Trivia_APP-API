import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from urllib.error import HTTPError

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request):
    items_limit = request.args.get('limit', 10, type=int)
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1

    questions = Question.query.order_by(
        Question.id
    ).limit(items_limit).offset(current_index * items_limit).all()

    questions_obj = [question.format() for question in questions]

    return questions_obj


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  #Completed: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  #Completed: Use the after_request decorator to set Access-Control-Allow
  '''

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route('/')
    @app.route('/categories')
    def retrieve_categories():
        # retrieve categories from db
        categories = Category.query.order_by(Category.id).all()
        # if no categories, throw not found error
        if len(categories) == 0:
            abort(404)
        # return json obj
        return jsonify({
            'success': True,
            # Note: for some reasons category.format() didn't work and throws an error
            'categories': {category.id: category.type for category in categories},
            'total_categories': len(categories)
        })

    '''
  Completed: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    @app.route('/questions')
    def retrieve_questions():
        # paginate questions to get the questions of curr page
        current_questions = paginate_questions(request)
        # get categories
        categories = Category.query.order_by(Category.type).all()
        # if no questions, throw not found error
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(current_questions),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })

    '''
  Completed 
  Create an endpoint to DELETE question using a question ID. 
  

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            # get question by id
            question = Question.query.get(question_id)
            # if question not found, throw not found error
            if question is None:
                abort(422)
            # delete the question
            question.delete()
            # recall the updated questions
            current_questions = paginate_questions(request)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(current_questions),
            })

        except (HTTPError, Exception):
            abort(422)

    '''
  @Completed: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @app.route("/questions", methods=['POST'])
    def add_question():

        body = request.get_json()

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        try:

            # populate the question object with the body data
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            if question is None:
                abort(422)
            # insert into db
            question.insert()
            # recall the updated questions
            current_questions = paginate_questions(request)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(current_questions),
            })

        except (HTTPError, Exception):
            abort(422)

    '''
    
  Completed: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        try:
            if len(search_term) == 0:
                abort(404)
            # query 'Question' table and filter on 'question' column based on the search term
            search_results = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })

        except (HTTPError, Exception):
            abort(404)

    '''
  Completed: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):

        try:
            # query the Question table and filter the category column based on the requested category
            questions_per_category = Question.query.filter(
                Question.category == str(category_id)).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions_per_category],
                'total_questions': len(questions_per_category),
                'current_category': category_id
            })
        except (HTTPError, Exception):
            abort(404)

    '''
  Completed: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        try:
            body = request.get_json()
            category = body['quiz_category']
            prev_questions = body['previous_questions']

            # if selected category is 'all', no filter by category is required
            if category['id'] == 0:
                questions = Question.query.filter(
                    # don't include prev questions
                    Question.id.notin_(prev_questions)).all()

            # else filter questions by the selected category
            else:
                questions = Question.query.filter_by(
                    category=category['id']).filter(
                    # don't include prev questions
                    Question.id.notin_(prev_questions)).all()

            new_question = questions[random.randrange(
                0, len(questions))].format() if len(questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })

        except (HTTPError, Exception):
            abort(404)

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app
