const record = document.querySelector('.record');
const stop = document.querySelector('.stop');
const soundClips = document.querySelector('.sound-clips');
const canvas = document.querySelector('.visualizer');
const mainSection = document.querySelector('.main-controls');

// Stop 버튼 비활성화 (녹음 중이 아닐 때)
stop.disabled = true;

// Web Audio API 및 Canvas 설정
let audioCtx;
const canvasCtx = canvas.getContext("2d");

// MediaRecorder 관련 변수
let mediaRecorder = null;
let chunks = [];

if (navigator.mediaDevices.getUserMedia) {
  console.log("getUserMedia supported.");

  const constraints = { audio: true };

  let onSuccess = function (stream) {
    visualize(stream); // 파형 분석 함수 실행

    function initializeRecorder() {
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        console.log("📡 녹음 종료, 서버에 전송 시작");

        const blob = new Blob(chunks, { type: "audio/ogg; codecs=opus" });
        chunks = []; // 배열 초기화
        const audioURL = URL.createObjectURL(blob);

        createAudioClip(audioURL, blob);
        await uploadAudio(blob);
      };
    }

    initializeRecorder();

    record.onclick = function () {
      if (!mediaRecorder || mediaRecorder.state === "inactive") {
        initializeRecorder();
      }
      mediaRecorder.start();
      console.log("🔴 녹음 시작");

      record.style.background = "red";
      stop.style.background = "green";

      stop.disabled = false;
      record.disabled = true;
    };

    stop.onclick = function () {
      if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        console.log("⏹️ 녹음 중지");

        record.style.background = "";
        stop.style.background = "";

        stop.disabled = true;
        record.disabled = false;
      }
    };
  };

  let onError = function (err) {
    console.error("🎤 마이크 접근 오류:", err);
  };

  navigator.mediaDevices.getUserMedia(constraints)
    .then((stream) => {
      window.streamReference = stream;
      onSuccess(stream);
    })
    .catch(onError);
} else {
  console.log("getUserMedia not supported on your browser!");
}

// 🎨 오디오 시각화 함수 (변경 없음)
function visualize(stream) {
  if (!audioCtx || audioCtx.state === "suspended") {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    audioCtx.resume();
  }

  const source = audioCtx.createMediaStreamSource(stream);
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  source.connect(analyser);

  function draw() {
    const WIDTH = canvas.width;
    const HEIGHT = canvas.height;

    requestAnimationFrame(draw);

    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = "rgb(200, 200, 200)";
    canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = "rgb(0, 0, 0)";

    canvasCtx.beginPath();

    let sliceWidth = (WIDTH * 1.0) / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      let v = dataArray[i] / 128.0;
      let y = v * HEIGHT / 2;

      if (i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height / 2);
    canvasCtx.stroke();
  }

  draw();
}

// 🛠 오디오 클립 생성 함수
function createAudioClip(audioURL, blob) {
  const clipName = prompt("Enter a name for your sound clip?", "My unnamed clip");

  const clipContainer = document.createElement("article");
  const clipLabel = document.createElement("p");
  const audio = document.createElement("audio");
  const deleteButton = document.createElement("button");

  clipContainer.classList.add("clip");
  audio.setAttribute("controls", "");
  deleteButton.textContent = "Delete";
  deleteButton.className = "delete";

  clipLabel.textContent = clipName || "My unnamed clip";

  clipContainer.appendChild(audio);
  clipContainer.appendChild(clipLabel);
  clipContainer.appendChild(deleteButton);
  soundClips.appendChild(clipContainer);

  audio.controls = true;
  audio.src = audioURL;

  deleteButton.onclick = function (e) {
    e.target.parentNode.remove();
  };

  clipLabel.onclick = function () {
    const newClipName = prompt("Enter a new name for your sound clip?");
    if (newClipName !== null) {
      clipLabel.textContent = newClipName;
    }
  };
}

// 📡 서버에 오디오 업로드
async function uploadAudio(audioBlob) {
  try {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.ogg");

    const serverURL = window.location.origin;
    const response = await fetch(`${serverURL}/upload`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      console.log("✅ 업로드 성공");
    } else {
      console.error("❌ 업로드 실패");
    }
  } catch (error) {
    console.error("📡 서버 전송 오류:", error);
  }
}

// 창 크기 변경 시 캔버스 크기 조정
window.onresize = function () {
  canvas.width = mainSection.offsetWidth;
};

window.onresize();
