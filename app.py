from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import base64
import torch

# Tạo ứng dụng Flask
app = Flask(__name__)

# Tải mô hình YOLO với trọng số được chỉ định
model = YOLO('best.pt')

# Hàm phát hiện đối tượng trong ảnh
def detect_objects(image, conf_thres=0.5, iou_thres=0.5):
    # Thực hiện phát hiện đối tượng
    results = model(image)
    for result in results:
        for bbox in result.boxes:
            # Lọc theo ngưỡng độ tin cậy
            if bbox.conf[0] >= conf_thres:
                x1, y1, x2, y2 = bbox.xyxy[0].cpu().numpy()  # Lấy toạ độ khung bao
                cls_id = int(bbox.cls[0])  # Lấy ID lớp
                label = model.names[cls_id]  # Lấy nhãn lớp
                confidence = bbox.conf[0].cpu().numpy()  # Lấy điểm độ tin cậy
                label_with_conf = f"{label} {confidence:.2f}"  # Kết hợp nhãn với độ tin cậy
                # Vẽ khung bao và nhãn lên ảnh
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(image, label_with_conf, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return image

# Route cho trang chủ
@app.route('/')
def index():
    return render_template('index.html')

# Route để xử lý tải lên tệp
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']  # Lấy tệp được tải lên
    if file:
        npimg = np.fromstring(file.read(), np.uint8)  # Chuyển đổi tệp thành mảng NumPy
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)  # Giải mã ảnh
        img = cv2.resize(img, (640, 480))  # Thay đổi kích thước ảnh để xử lý nhanh hơn
        result_img = detect_objects(img)  # Phát hiện đối tượng trong ảnh
        _, img_encoded = cv2.imencode('.jpg', result_img)  # Mã hoá ảnh kết quả thành JPEG
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')  # Mã hoá ảnh JPEG thành base64
        return jsonify({'image': img_base64})  # Trả lại ảnh base64
    return 'No file uploaded', 400

# Route để xử lý ảnh từ webcam
@app.route('/webcam', methods=['POST'])
def webcam():
    data = request.get_json()  # Lấy dữ liệu JSON từ yêu cầu
    img_base64 = data['image']  # Lấy chuỗi ảnh base64
    img_data = base64.b64decode(img_base64)  # Giải mã ảnh base64
    npimg = np.frombuffer(img_data, np.uint8)  # Chuyển đổi ảnh đã giải mã thành mảng NumPy
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)  # Giải mã ảnh
    img = cv2.resize(img, (640, 480))  # Thay đổi kích thước ảnh để xử lý nhanh hơn
    result_img = detect_objects(img)  # Phát hiện đối tượng trong ảnh
    _, img_encoded = cv2.imencode('.jpg', result_img)  # Mã hoá ảnh kết quả thành JPEG
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')  # Mã hoá ảnh JPEG thành base64
    return jsonify({'image': img_base64})  # Trả lại ảnh base64

# Chạy ứng dụng Flask
if __name__ == '__main__':
    # Kiểm tra xem GPU có sẵn không và in ra thiết bị đang được sử dụng
    if torch.cuda.is_available():
        print("Using GPU")
    else:
        print("Using CPU")
    app.run(debug=True)
