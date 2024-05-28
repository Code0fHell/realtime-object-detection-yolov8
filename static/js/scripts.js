document.getElementById('upload').addEventListener('change', function() {
    const file = this.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const img = document.getElementById('output');
        img.src = 'data:image/jpeg;base64,' + data.image;
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('webcamButton').addEventListener('click', function() {
    const video = document.getElementById('webcam');
    const constraints = {
        video: { width: 640, height: 480 }
    };

    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            video.srcObject = stream;
            setInterval(() => {
                captureFrame(video);
            }, 500);  // Reduce interval to increase FPS
        })
        .catch(error => console.error('Error:', error));
});

function captureFrame(video) {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg');
    const base64 = dataUrl.split(',')[1];

    fetch('/webcam', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: base64 })
    })
    .then(response => response.json())
    .then(data => {
        const img = document.getElementById('output');
        img.src = 'data:image/jpeg;base64,' + data.image;
    })
    .catch(error => console.error('Error:', error));
}
