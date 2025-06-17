from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from PIL import Image
import base64

app = Flask(name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель базы данных для хранения изображений
class ImageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    data = db.Column(db.LargeBinary)

db.create_all()

# 1. Добавление изображения (POST /api/image/add)
@app.route('/api/image/add', methods=['POST'])
def add_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    filename = file.filename
    image_data = file.read()
    
    new_image = ImageModel(filename=filename, data=image_data)
    db.session.add(new_image)
    db.session.commit()
    
    return jsonify({'message': 'Image added', 'id': new_image.id}), 201

# 2. Изменение размера изображения (PUT /api/image/change/size)
@app.route('/api/image/change/size', methods=['PUT'])
def change_image_size():
    data = request.get_json()
    image_id = data.get('id')
    new_width = data.get('width')
    new_height = data.get('height')
    
    if not all([image_id, new_width, new_height]):
        return jsonify({'error': 'Missing parameters'}), 400
    
    image_record = ImageModel.query.get(image_id)
    if not image_record:
        return jsonify({'error': 'Image not found'}), 404
    
    # Работа с изображением
    image_stream = BytesIO(image_record.data)
    with Image.open(image_stream) as img:
        resized_img = img.resize((new_width, new_height))
        output_stream = BytesIO()
        resized_img.save(output_stream, format=img.format)
        output_stream.seek(0)
        image_record.data = output_stream.read()
    
    db.session.commit()
    
    return jsonify({'message': 'Image resized'}), 200

# 3. Поворот изображения (PUT /api/image/change/rotate)
@app.route('/api/image/change/rotate', methods=['PUT'])
def rotate_image():
    data = request.get_json()
    image_id = data.get('id')
    degrees = data.get('degrees')
    
    if not all([image_id, degrees]):
        return jsonify({'error': 'Missing parameters'}), 400
    
    image_record = ImageModel.query.get(image_id)
    if not image_record:
        return jsonify({'error': 'Image not found'}), 404
    
    # Работа с изображением
    image_stream = BytesIO(image_record.data)
    with Image.open(image_stream) as img:
        rotated_img = img.rotate(degrees, expand=True)
        output_stream = BytesIO()
        rotated_img.save(output_stream, format=img.format)
        output_stream.seek(0)
        image_record.data = output_stream.read()
    
    db.session.commit()
    
    return jsonify({'message': 'Image rotated'}), 200

# 4. Получить все изображения (GET /api/image)
@app.route('/api/image', methods=['GET'])
def get_all_images():
    images = ImageModel.query.all()