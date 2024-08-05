let audioChunks = [];
let mediaRecorder;

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true, video: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            document.getElementById('video').srcObject = stream;

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                var today = getTodayDateTimeString();

                captureImage('canvas', 'video')
                    .then(imageData => fetch(imageData))
                    .then(res => res.blob())
                    .then(blob => {
                        const formData = new FormData();
                        formData.append("audioFile", audioBlob, today + ".wav");
                        formData.append("imageFile", blob, today + ".png");

                        fetch('/upload', {
                            method: 'POST',
                            body: formData
                        })
                            .then(response => response.json())
                            .then(data => {
                                if (data.message === "Uploaded successfully") {
                                    document.getElementById('result').innerText = data.text;
                                } else {
                                    document.getElementById('result').innerText = "Failed to upload";
                                }
                            })
                            .catch(error => {
                                console.error('업로드 중 오류 발생:', error);
                                document.getElementById('result').innerText = "업로드 중 오류 발생.";
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
    document.getElementById('recording').disabled = false;
    mediaRecorder.stop();

    document.getElementById('recording').removeEventListener('click', stopRecording);
    document.getElementById('recording').addEventListener('click', startRecording);
}

document.getElementById('recording').addEventListener('click', startRecording);

function captureImage(canvasId, videoId) {
    return new Promise((resolve, reject) => {
        try {
            const canvas = document.getElementById(canvasId);
            const video = document.getElementById(videoId);
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/png');
            resolve(imageData);
        } catch (error) {
            reject(error);
        }
    });
}

function getTodayDateTimeString() {
    var today = new Date();
    var year = today.getFullYear();
    var month = today.getMonth() + 1;
    var day = today.getDate();
    var hours = today.getHours();
    var minutes = today.getMinutes();
    var seconds = today.getSeconds();

    if (month < 10) { month = '0' + month; }
    if (day < 10) { day = '0' + day; }
    if (hours < 10) { hours = '0' + hours; }
    if (minutes < 10) { minutes = '0' + minutes; }
    if (seconds < 10) { seconds = '0' + seconds; }

    return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
}
