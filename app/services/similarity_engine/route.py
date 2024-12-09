from flask import Blueprint, jsonify, make_response, request

text_similarity = Blueprint('TextSimilarity', __name__)


@text_similarity.route("/")
def text_similarity_home():
    return "<h1>Similarity Home</h1>"


@text_similarity.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)





@text_similarity.route('/', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
