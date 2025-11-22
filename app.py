from flask import Flask, render_template, request, jsonify
from agents.parent import ParentAgent

app = Flask(__name__)
agent = ParentAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    if not user_message:
        return jsonify({'response': 'Please enter a message.'}), 400
    
    response = agent.process_message(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
