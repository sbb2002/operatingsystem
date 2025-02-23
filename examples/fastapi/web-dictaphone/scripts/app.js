// const record = document.querySelector('.record');
// const stop = document.querySelector('.stop');
// const soundClips = document.querySelector('.sound-clips');
// const canvas = document.querySelector('.visualizer');
// const mainSection = document.querySelector('.main-controls');

// stop.disabled = true;

// let audioCtx;
// const canvasCtx = canvas.getContext("2d");

// // 오디오 캡처 및 처리 함수
// if (navigator.mediaDevices.getUserMedia) {
//   console.log('getUserMedia supported.');

//   const constraints = { audio: true };
//   let chunks = [];

//   let onSuccess = function(stream) {
//     // 48kHz로 오디오 컨텍스트 초기화
//     audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
//     const analyser = audioCtx.createAnalyser();
//     const source = audioCtx.createMediaStreamSource(stream);
//     source.connect(analyser);

//     const bufferLength = analyser.frequencyBinCount;
//     const dataArray = new Uint8Array(bufferLength);

//     // 캔버스 시각화
//     visualize(stream);

//     // 미디어 레코더 대신 Web Audio API를 사용하여 오디오 처리
//     const processor = audioCtx.createScriptProcessor(2048, 1, 1); // 2048 샘플 크기 설정
//     analyser.connect(processor);
//     processor.connect(audioCtx.destination);

//     let isRecording = false;

//     record.onclick = function() {
//       isRecording = true;
//       console.log("Recording started...");
//       record.style.background = "red";
//       stop.disabled = false;
//       record.disabled = true;
//     };

//     stop.onclick = function() {
//       isRecording = false;
//       console.log("Recording stopped.");
//       record.style.background = "";
//       stop.disabled = true;
//       record.disabled = false;
//     };

//     // ScriptProcessor를 통해 오디오 데이터를 처리
//     processor.onaudioprocess = function(e) {
//       if (!isRecording) return;

//       const inputData = e.inputBuffer.getChannelData(0); // 1채널 오디오 데이터
//       const outputData = convertTo16Bit(inputData); // 16비트로 변환

//       // 데이터를 녹음할 배열에 추가
//       chunks.push(outputData);

//       // 캔버스 시각화 업데이트
//       analyser.getByteFrequencyData(dataArray);
//       drawVisualizer(dataArray);
//     };

//     // 오디오 데이터를 16비트로 변환
//     function convertTo16Bit(inputArray) {
//       const outputArray = new Int16Array(inputArray.length);
//       for (let i = 0; i < inputArray.length; i++) {
//         outputArray[i] = Math.max(-32768, Math.min(32767, inputArray[i] * 32767)); // 16비트로 스케일링
//       }
//       return outputArray;
//     }

//     // 캔버스를 통한 시각화
//     function drawVisualizer(dataArray) {
//       const WIDTH = canvas.width;
//       const HEIGHT = canvas.height;
//       canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
//       canvasCtx.fillStyle = 'rgb(200, 200, 200)';
//       canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
//       canvasCtx.lineWidth = 2;
//       canvasCtx.strokeStyle = 'rgb(0, 0, 0)';
//       canvasCtx.beginPath();

//       const sliceWidth = WIDTH * 1.0 / dataArray.length;
//       let x = 0;

//       for (let i = 0; i < dataArray.length; i++) {
//         let v = dataArray[i] / 128.0;
//         let y = v * HEIGHT / 2;

//         if (i === 0) {
//           canvasCtx.moveTo(x, y);
//         } else {
//           canvasCtx.lineTo(x, y);
//         }

//         x += sliceWidth;
//       }

//       canvasCtx.lineTo(canvas.width, canvas.height / 2);
//       canvasCtx.stroke();
//     }

//     // 녹음이 끝났을 때 클립을 생성하고 출력
//     stop.onclick = function() {
//       const clipName = prompt('Enter a name for your sound clip?', 'My unnamed clip');
//       const clipContainer = document.createElement('article');
//       const clipLabel = document.createElement('p');
//       const audio = document.createElement('audio');
//       const deleteButton = document.createElement('button');

//       clipContainer.classList.add('clip');
//       audio.setAttribute('controls', '');
//       deleteButton.textContent = 'Delete';
//       deleteButton.className = 'delete';

//       clipLabel.textContent = clipName || 'My unnamed clip';

//       clipContainer.appendChild(audio);
//       clipContainer.appendChild(clipLabel);
//       clipContainer.appendChild(deleteButton);
//       soundClips.appendChild(clipContainer);

//       // 16비트로 변환된 데이터를 Blob으로 처리
//       const blob = new Blob([new Int16Array(chunks.flat())], { type: 'audio/wav' });
//       const audioURL = URL.createObjectURL(blob);
//       audio.src = audioURL;

//       // 삭제 버튼 클릭 시 클립 삭제
//       deleteButton.onclick = function(e) {
//         e.target.parentNode.remove();
//       };
//     };
//   }

//   let onError = function(err) {
//     console.log('The following error occured: ' + err);
//   };

//   navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);

// } else {
//   console.log('getUserMedia not supported on your browser!');
// }

// // 화면 리사이즈에 맞춰 캔버스 크기 조정
// window.onresize = function() {
//   canvas.width = mainSection.offsetWidth;
// };
// window.onresize();

// ###
// set up basic variables for app

const record = document.querySelector('.record');
const stop = document.querySelector('.stop');
const soundClips = document.querySelector('.sound-clips');
const canvas = document.querySelector('.visualizer');
const mainSection = document.querySelector('.main-controls');

// disable stop button while not recording

stop.disabled = true;

// visualiser setup - create web audio api context and canvas

let audioCtx;
const canvasCtx = canvas.getContext("2d");

//main block for doing the audio recording

if (navigator.mediaDevices.getUserMedia) {
  console.log('getUserMedia supported.');

  const constraints = { audio: true };
  let chunks = [];

  let onSuccess = function(stream) {
    const mediaRecorder = new MediaRecorder(stream);

    visualize(stream);

    record.onclick = function() {
      mediaRecorder.start();
      console.log(mediaRecorder.state);
      console.log("recorder started");
      record.style.background = "red";

      setInterval(() => {
        if (mediaRecorder.state === 'inactive') {
            mediaRecorder.start();  // 중간에 멈추지 않도록 주기적으로 상태 확인
        }
    }, 1000);  // 5초마다 확인

      stop.disabled = false;
      record.disabled = true;
    }

    stop.onclick = function() {
      mediaRecorder.stop();
      console.log(mediaRecorder.state);
      console.log("recorder stopped");
      record.style.background = "";
      record.style.color = "";
      // mediaRecorder.requestData();

      stop.disabled = true;
      record.disabled = false;
    }

    mediaRecorder.onstop = function(e) {
      console.log("data available after MediaRecorder.stop() called.");

      const clipName = prompt('Enter a name for your sound clip?','My unnamed clip');

      const clipContainer = document.createElement('article');
      const clipLabel = document.createElement('p');
      const audio = document.createElement('audio');
      const deleteButton = document.createElement('button');

      clipContainer.classList.add('clip');
      audio.setAttribute('controls', '');
      deleteButton.textContent = 'Delete';
      deleteButton.className = 'delete';

      if(clipName === null) {
        clipLabel.textContent = 'My unnamed clip';
      } else {
        clipLabel.textContent = clipName;
      }

      clipContainer.appendChild(audio);
      clipContainer.appendChild(clipLabel);
      clipContainer.appendChild(deleteButton);
      soundClips.appendChild(clipContainer);

      audio.controls = true;
      const blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
      chunks = [];
      const audioURL = window.URL.createObjectURL(blob);
      audio.src = audioURL;
      console.log("recorder stopped");

      deleteButton.onclick = function(e) {
        let evtTgt = e.target;
        evtTgt.parentNode.parentNode.removeChild(evtTgt.parentNode);
      }

      clipLabel.onclick = function() {
        const existingName = clipLabel.textContent;
        const newClipName = prompt('Enter a new name for your sound clip?');
        if(newClipName === null) {
          clipLabel.textContent = existingName;
        } else {
          clipLabel.textContent = newClipName;
        }
      }
    }

    mediaRecorder.ondataavailable = function(e) {
      chunks.push(e.data);
    }
  }

  let onError = function(err) {
    console.log('The following error occured: ' + err);
  }

  // navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);
  navigator.mediaDevices.getUserMedia(constraints).then(stream => {
    window.streamReference = stream;  // 전역 변수로 스트림 유지
    onSuccess(stream);
}).catch(onError);


} else {
   console.log('getUserMedia not supported on your browser!');
}

function visualize(stream) {
  // if(!audioCtx) {
  //   audioCtx = new AudioContext();
  // }
  if (!audioCtx || audioCtx.state === 'suspended') {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    audioCtx.resume();  // AudioContext 활성화
}


  
  const source = audioCtx.createMediaStreamSource(stream);

  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  source.connect(analyser);
  //analyser.connect(audioCtx.destination);

  draw()

  function draw() {
    const WIDTH = canvas.width
    const HEIGHT = canvas.height;

    requestAnimationFrame(draw);

    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = 'rgb(200, 200, 200)';
    canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

    canvasCtx.beginPath();

    let sliceWidth = WIDTH * 1.0 / bufferLength;
    let x = 0;


    for(let i = 0; i < bufferLength; i++) {

      let v = dataArray[i] / 128.0;
      let y = v * HEIGHT/2;

      if(i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height/2);
    canvasCtx.stroke();

  }
}

window.onresize = function() {
  canvas.width = mainSection.offsetWidth;
}

window.onresize();
