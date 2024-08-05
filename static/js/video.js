let audioChunks = [];
let mediaRecorder;

function startCamera() {
    const video = document.getElementById('video');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            console.error("Error accessing the camera: ", err);
        });
}

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                const today = getTodayDateTimeString();
                formData.append("audioFile", audioBlob, today + ".wav");

                fetch('/upload_audio', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message === "Uploaded successfully") {
                        document.getElementById('result').innerText = data.text;
                    } else {
                        document.getElementById('result').innerText = "Failed to upload audio";
                    }
                })
                .catch(error => {
                    console.error('Audio upload error:', error);
                    document.getElementById('result').innerText = "Audio upload error.";
                });

                audioChunks = [];
            };

            mediaRecorder.start();
            document.getElementById('recording').removeEventListener('click', startRecording);
            document.getElementById('recording').addEventListener('click', stopRecording);
        })
        .catch(console.error);
}

function stopRecording() {
    mediaRecorder.stop();
    document.getElementById('recording').removeEventListener('click', stopRecording);
    document.getElementById('recording').addEventListener('click', startRecording);
}

function captureImage() {
    const canvas = document.getElementById('canvas');
    const video = document.getElementById('video');
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');
    const today = getTodayDateTimeString();
    const formData = new FormData();
    formData.append("imageFile", dataURLtoBlob(imageData), today + ".png");

    fetch('/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Uploaded successfully") {
            document.getElementById('result').innerText = "Image uploaded successfully";
        } else {
            document.getElementById('result').innerText = "Failed to upload image";
        }
    })
    .catch(error => {
        console.error('Image upload error:', error);
        document.getElementById('result').innerText = "Image upload error.";
    });
}

function dataURLtoBlob(dataURL) {
    const byteString = atob(dataURL.split(',')[1]);
    const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

function getTodayDateTimeString() {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth() + 1;
    const day = today.getDate();
    const hours = today.getHours();
    const minutes = today.getMinutes();
    const seconds = today.getSeconds();

    return `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

document.getElementById('capture').addEventListener('click', captureImage);
document.getElementById('recording').addEventListener('click', startRecording);

window.onload = startCamera;
