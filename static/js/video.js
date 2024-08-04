// JavaScript to access the user's webcam and display it in the video element
const video = document.getElementById('video');
const fallbackImage = document.getElementById('fallbackImage');

// Check if the browser supports getUserMedia
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(function (stream) {
      video.srcObject = stream;
      video.style.display = 'block';
      fallbackImage.style.display = 'none';
    })
    .catch(function (err) {
      console.error("Error accessing the camera: " + err);
      video.style.display = 'none';
      fallbackImage.style.display = 'block';
    });
} else {
  alert('Your browser does not support accessing the camera.');
  video.style.display = 'none';
  fallbackImage.style.display = 'block';
}


// Check if the browser supports getUserMedia for video
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(function (stream) {
      video.srcObject = stream;

      let mediaRecorder;
      let audioChunks = [];
      let isRecording = false;

      // Toggle recording state on image click
      document.getElementById('questionImage').addEventListener('click', () => {
        if (!isRecording) {
          // Start recording
          mediaRecorder = new MediaRecorder(stream);
          audioChunks = [];
          mediaRecorder.start();
          isRecording = true;
          console.log('Recording started.');

          mediaRecorder.ondataavailable = function (event) {
            audioChunks.push(event.data);
          };

          mediaRecorder.onstop = function () {
            console.log('Recording stopped.');
            const audioBlob = new Blob(audioChunks, { 'type': 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.play(); 
          };

        } else {
          mediaRecorder.stop();
          isRecording = false;
          console.log('Recording stopped manually.');
        }
      });
    })
    .catch(function (err) {
      console.error("Error accessing the camera: " + err);
    });
} else {
  alert('Your browser does not support accessing the camera or microphone.');
}

// Detect device orientation change
window.addEventListener('orientationchange', function () {
  let transformValue = '';
  switch (window.orientation) {
    case 0:
      transformValue = 'scaleX(-1) rotate(0deg)';
      break;
    case 90:
      transformValue = 'scaleX(-1) rotate(-90deg)';
      break;
    case -90:
      transformValue = 'scaleX(-1) rotate(90deg)';
      break;
    case 180:
      transformValue = 'scaleX(-1) rotate(180deg)';
      break;
  }
  video.style.transform = transformValue;
});