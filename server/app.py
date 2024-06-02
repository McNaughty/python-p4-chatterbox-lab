from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET','POST'])
def messages():
    if request.method == 'GET':

        # Query all messages ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()
        
        # Convert each message to a dictionary using list comprehension
        all_messages = [message.to_dict() for message in messages]
        
        # Create a response with JSON data
        response = make_response(
            jsonify(all_messages),
            200
        )

        return response
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'body' not in data or 'username' not in data:
            return make_response(jsonify({'error': 'Invalid input'}), 400)
        
        new_message = Message(
            body = data['body'],
            username = data['username']
        )

        db.session.add(new_message)
        db.session.commit()

        response = make_response(
            jsonify(new_message.to_dict()),
            201
        )
        return response


@app.route('/messages/<int:id>', methods = ['PATCH'])
def messages_by_id(id):
    data = request.get_json()
    if not data or 'body' not in data:
        return make_response(jsonify({'error':'Invalid input'}), 400)
    
    message = Message.query.get(id)
    if message is None:
        return make_response(jsonify({'error': 'Message notfound'}), 404)

    message.body = data['body']
    db.session.commit()

    response = make_response(
        jsonify(message.to_dict()),
        200
    )
    return response

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if message is None:
        return make_response(jsonify({'error': 'Message not found'}), 404)
    
    db.session.delete(message)
    db.session.commit()
    
    # Verify the message is deleted
    deleted_message = Message.query.get(id)
    if deleted_message is not None:
        return make_response(jsonify({'error': 'Message not deleted'}), 500)
    
    response = make_response(
        jsonify({'message': 'Message deleted successfully'}),
        200
    )
    return response

if __name__ == '__main__':
    app.run(port=5555)
