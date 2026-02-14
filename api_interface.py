from flask import Flask, request, jsonify
from main_controller import StarkAssistant
import config
from datetime import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize assistant instance
assistant = StarkAssistant(config.DEFAULT_USER_ID)

# Health Check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check API health status"""
    return jsonify({
        'status': 'healthy',
        'service': config.APP_NAME,
        'version': config.APP_VERSION,
        'timestamp': datetime.now().isoformat()
    }), 200

# Task Management Endpoints
@app.route('/api/task/add', methods=['POST'])
def add_task():
    """Add a new task"""
    try:
        data = request.get_json()
        task_name = data.get('task_name')
        due_date = data.get('due_date', None)
        
        if not task_name:
            return jsonify({'error': 'task_name is required'}), 400
        
        result = assistant.process_command('add_task', task_name, due_date)
        return jsonify({'message': result, 'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/task/list', methods=['GET'])
def list_tasks():
    """List all tasks for the user"""
    try:
        tasks = assistant.process_command('list_tasks')
        return jsonify({'tasks': tasks, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/task/complete/<int:task_id>', methods=['PUT'])
def complete_task(task_id):
    """Mark a task as completed"""
    try:
        result = assistant.process_command('complete_task', task_id)
        return jsonify({'message': result, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/task/delete/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        result = assistant.process_command('delete_task', task_id)
        return jsonify({'message': result, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/task/overdue', methods=['GET'])
def get_overdue_tasks():
    """Get overdue tasks"""
    try:
        tasks = assistant.process_command('get_overdue_tasks')
        return jsonify({'tasks': tasks, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

# Communication Endpoints
@app.route('/api/message/send', methods=['POST'])
def send_message():
    """Send a message"""
    try:
        data = request.get_json()
        recipient = data.get('recipient')
        message = data.get('message')
        
        if not recipient or not message:
            return jsonify({'error': 'recipient and message are required'}), 400
        
        result = assistant.process_command('send_message', recipient, message)
        return jsonify({'message': result, 'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/message/list', methods=['GET'])
def get_messages():
    """Get all messages for the user"""
    try:
        messages = assistant.process_command('get_messages')
        return jsonify({'messages': messages, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/notification/send', methods=['POST'])
def send_notification():
    """Send a notification"""
    try:
        data = request.get_json()
        notification = data.get('notification')
        notification_type = data.get('type', 'notification')
        
        if not notification:
            return jsonify({'error': 'notification is required'}), 400
        
        result = assistant.process_command('send_notification', notification, notification_type)
        return jsonify({'message': result, 'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/notification/list', methods=['GET'])
def get_notifications():
    """Get all notifications"""
    try:
        notifications = assistant.process_command('get_notifications')
        return jsonify({'notifications': notifications, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

# Memory Management Endpoints
@app.route('/api/memory/store', methods=['POST'])
def store_memory():
    """Store user memory"""
    try:
        data = request.get_json()
        category = data.get('category')
        key = data.get('key')
        value = data.get('value')
        
        if not category or not key:
            return jsonify({'error': 'category and key are required'}), 400
        
        result = assistant.process_command('store_memory', category, key, value)
        return jsonify({'message': result, 'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/memory/retrieve/<category>', methods=['GET'])
def retrieve_memory(category):
    """Retrieve memories by category"""
    try:
        memories = assistant.process_command('retrieve_memory', category)
        return jsonify({'memories': memories, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/memory/search', methods=['POST'])
def search_memories():
    """Search memories by keyword"""
    try:
        data = request.get_json()
        keyword = data.get('keyword')
        
        if not keyword:
            return jsonify({'error': 'keyword is required'}), 400
        
        results = assistant.process_command('search_memories', keyword)
        return jsonify({'results': results, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

# System Endpoints
@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall system status"""
    try:
        status = assistant.get_status()
        return jsonify({'status': status}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute a custom command"""
    try:
        data = request.get_json()
        command = data.get('command')
        args = data.get('args', [])
        
        if not command:
            return jsonify({'error': 'command is required'}), 400
        
        result = assistant.process_command(command, *args)
        return jsonify({'result': result, 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found', 'status': 'error'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error', 'status': 'error'}), 500

if __name__ == '__main__':
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.API_DEBUG)