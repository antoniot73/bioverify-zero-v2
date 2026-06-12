const consent = document.getElementById("consent");
const documentImage = document.getElementById("documentImage");
const startCameraButton = document.getElementById("startCamera");
const captureFrameButton = document.getElementById("captureFrame");
const verifyButton = document.getElementById("verify");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const result = document.getElementById("result");
const captureStatus = document.getElementById("captureStatus");

let liveImageDataUrl = null;
let mediaStream = null;

function updateControls() {
  const hasConsent = consent.checked;
  const hasDocument = documentImage.files.length === 1;
  startCameraButton.disabled = !hasConsent;
  verifyButton.disabled = !(hasConsent && hasDocument && liveImageDataUrl);
}

async function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("No fue posible leer el archivo."));

    reader.readAsDataURL(file);
  });
}

async function startCamera() {
  try {
    if (!consent.checked) {
      throw new Error("Debe aceptar el consentimiento antes de activar la cámara.");
    }

    mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = mediaStream;
    captureFrameButton.disabled = false;
    captureStatus.textContent = "Cámara activa.";
  } catch (error) {
    captureStatus.textContent = `Error: ${error.message}`;
  }
}

function captureFrame() {
  const context = canvas.getContext("2d");
  canvas.width = video.videoWidth || 480;
  canvas.height = video.videoHeight || 360;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  liveImageDataUrl = canvas.toDataURL("image/jpeg", 0.8);
  captureStatus.textContent = "Fotograma capturado localmente.";
  updateControls();
}

async function verifyIdentity() {
  try {
    result.textContent = "Procesando...";

    const documentDataUrl = await readFileAsDataUrl(documentImage.files[0]);

    const response = await fetch("/api/v1/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        consent_accepted: consent.checked,
        document_image_b64: documentDataUrl,
        live_image_b64: liveImageDataUrl
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Error de verificación.");
    }

    result.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
  }
}

consent.addEventListener("change", updateControls);
documentImage.addEventListener("change", updateControls);
startCameraButton.addEventListener("click", startCamera);
captureFrameButton.addEventListener("click", captureFrame);
verifyButton.addEventListener("click", verifyIdentity);

updateControls();
