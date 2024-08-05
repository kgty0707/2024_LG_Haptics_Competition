let audioChunks = [];
let mediaRecorder;
let originalImageSrc;

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
    originalImageSrc = document.getElementById('recording').src;
    document.getElementById('recording').src = "/static/images/질문중.png";
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const today = getTodayDateTimeString();
                
                captureImage().then(imageBlob => {
                    const formData = new FormData();
                    formData.append("audioFile", audioBlob, today + ".wav");
                    formData.append("imageFile", imageBlob, today + ".png");

                    fetch('/uploads', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message === "Uploaded successfully") {
                            displayServerResponse(data.result || "서버에서 받은 응답이 없습니다.");
                            playAudio(data.audio_url);
                        } else {
                            console.log("Failed to upload");
                        }
                        resetRecordingImage();
                    })
                    .catch(error => {
                        console.error('Upload error:', error);
                        console.log("Upload error.");
                        resetRecordingImage();
                    });

                    audioChunks = [];
                });
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
    return new Promise((resolve, reject) => {
        const canvas = document.getElementById('canvas');
        const video = document.getElementById('video');
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/png');
        resolve(dataURLtoBlob(imageData));
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

function displayServerResponse(responseText) {
    const introText = document.getElementById('intro-text');
    const questionsList = document.getElementById('questions-list');
    const serverResponse = document.getElementById('server-response');

    introText.style.display = 'none';
    questionsList.style.display = 'none';
    serverResponse.style.display = 'block';

    responseText = responseText.replace(/\\n/g, '<br>');

    serverResponse.innerHTML = marked.parse(responseText);
}

function playAudio(audioUrl) {
    const audioPlayer = document.getElementById('audio-player');
    audioPlayer.src = audioUrl;
    audioPlayer.style.display = 'block';
    audioPlayer.play();
}

function resetRecordingImage() {
    document.getElementById('recording').src = originalImageSrc;
}

document.getElementById('recording').addEventListener('click', startRecording);

window.onload = startCamera;
