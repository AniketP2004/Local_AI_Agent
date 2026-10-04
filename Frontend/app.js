// let mediaRecorder;
// let chunks = [];

// async function startRecording() {
//   const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//   mediaRecorder = new MediaRecorder(stream);
//   chunks = [];
//   mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
//   mediaRecorder.start();
// }

// async function stopRecording(sessionId, questionId) {
//   return new Promise((resolve) => {
//     mediaRecorder.onstop = async () => {
//       const blob = new Blob(chunks, { type: "audio/webm" });
//       const formData = new FormData();
//       formData.append("audio", blob, "answer.webm");

//       const res = await fetch(
//         `/session/${sessionId}/answer/voice?question_id=${questionId}`,
//         { method: "POST", body: formData }
//       );
//       resolve(await res.json());
//     };
//     mediaRecorder.stop();
//   });
// }

// async function loadDashboard() {
//   const res = await fetch("/dashboard");
//   const data = await res.json();

//   const container = document.getElementById("dashboard");
//   container.innerHTML = data.stats
//     .map(s => `
//       <div class="topic-row ${data.weak_topics.includes(s.topic) ? 'weak' : ''}">
//         <span>${s.topic}</span>
//         <span>${s.correct}/${s.total} (${s.accuracy}%)</span>
//       </div>
//     `)
//     .join("");
// }