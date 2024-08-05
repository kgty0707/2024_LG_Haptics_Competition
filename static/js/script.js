// 함수: 카메라 시작
function startCamera(videoElement) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoElement.srcObject = stream;
        })
        .catch(err => {
            console.error("Error accessing the camera: ", err);
        });
}

// 함수: 현재 프레임 캡쳐
function captureFrame(videoElement, canvasElement) {
    const context = canvasElement.getContext('2d');
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
    return canvasElement.toDataURL('image/png');
}

// 함수: 서버로 이미지 전송
function sendImageToServer(dataURL, url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: dataURL })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// 초기화 함수
function initialize() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureButton = document.getElementById('capture');

    startCamera(video);

    captureButton.addEventListener('click', () => {
        const dataURL = captureFrame(video, canvas);
        sendImageToServer(dataURL, 'http://127.0.0.1:8000/upload');
    });
}

// 페이지 로드 시 초기화 함수 실행
window.onload = initialize;
