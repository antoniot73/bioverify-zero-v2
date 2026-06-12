const adultConsent = document.getElementById("adultConsent");
const consent = document.getElementById("consent");
const documentImage = document.getElementById("documentImage");
const startCameraButton = document.getElementById("startCamera");
const captureFrameButton = document.getElementById("captureFrame");
const verifyButton = document.getElementById("verify");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const result = document.getElementById("result");
const captureStatus = document.getElementById("captureStatus");
const decisionLabel = document.getElementById("decisionLabel");

let liveImageDataUrl = null;
let mediaStream = null;
let isCameraReady = false;

/**
 * Actualiza el estado de los controles de la interfaz.
 */
function updateControls() {
  const hasAdultDeclaration = adultConsent.checked;
  const hasConsent = consent.checked;
  const hasLegalAcceptance = hasAdultDeclaration && hasConsent;
  const hasDocument = documentImage.files.length === 1;
  const hasLiveCapture = Boolean(liveImageDataUrl);

  startCameraButton.disabled = !hasLegalAcceptance;
  captureFrameButton.disabled = !(hasLegalAcceptance && isCameraReady);
  verifyButton.disabled = !(hasLegalAcceptance && hasDocument && hasLiveCapture);
}

/**
 * Limpia el resultado visible.
 */
function clearResult() {
  result.textContent = "";
  resetDecisionLabel();
}

/**
 * Restablece la etiqueta resumida del resultado.
 */
function resetDecisionLabel() {
  decisionLabel.textContent = "Resultado: sin verificar";
  decisionLabel.className = "result-line result-pending";
}

/**
 * Muestra al lado del título el resultado operativo de la verificación.
 *
 * @param {string} decision Decisión devuelta por el backend.
 */
function setDecisionLabel(decision) {
  const normalizedDecision = String(decision || "").toLowerCase();

  if (normalizedDecision === "match") {
    decisionLabel.textContent = "Resultado: match";
    decisionLabel.className = "result-line result-match";
    return;
  }

  if (normalizedDecision === "no_match" || normalizedDecision === "no match") {
    decisionLabel.textContent = "Resultado: no match";
    decisionLabel.className = "result-line result-no-match";
    return;
  }

  decisionLabel.textContent = "Resultado: no match";
  decisionLabel.className = "result-line result-no-match";
}

/**
 * Limpia la captura facial local.
 */
function clearLiveCapture() {
  liveImageDataUrl = null;
  canvas.hidden = true;

  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width || 1, canvas.height || 1);

  updateControls();
}

/**
 * Detiene la cámara y libera el dispositivo.
 */
function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
  }

  mediaStream = null;
  isCameraReady = false;
  video.srcObject = null;
  captureFrameButton.disabled = true;

  updateControls();
}

/**
 * Lee un archivo local como Data URL.
 *
 * @param {File} file Archivo seleccionado por el usuario.
 * @returns {Promise<string>} Contenido codificado como Data URL.
 */
async function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("No fue posible leer el archivo."));

    reader.readAsDataURL(file);
  });
}

/**
 * Espera a que el elemento de video tenga dimensiones válidas.
 *
 * @param {HTMLVideoElement} videoElement Elemento de video.
 * @returns {Promise<void>}
 */
async function waitForVideoReady(videoElement) {
  if (videoElement.videoWidth > 0 && videoElement.videoHeight > 0) {
    return;
  }

  await new Promise((resolve, reject) => {
    const timeoutId = window.setTimeout(() => {
      reject(new Error("La cámara tardó demasiado en iniciar."));
    }, 8000);

    videoElement.onloadedmetadata = () => {
      window.clearTimeout(timeoutId);
      resolve();
    };
  });

  if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {
    await new Promise((resolve) => window.setTimeout(resolve, 300));
  }

  if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {
    throw new Error("El video aún no tiene dimensiones válidas.");
  }
}

/**
 * Activa la cámara del usuario y prepara la captura.
 */
async function startCamera() {
  try {
    clearResult();
    clearLiveCapture();
    stopCamera();

    if (!adultConsent.checked) {
      throw new Error("Debe declarar que es mayor de edad antes de activar la cámara.");
    }

    if (!consent.checked) {
      throw new Error("Debe aceptar el consentimiento antes de activar la cámara.");
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error("El navegador no soporta acceso a cámara mediante getUserMedia.");
    }

    captureStatus.textContent = "Solicitando acceso a la cámara...";

    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: "user"
      },
      audio: false
    });

    video.muted = true;
    video.playsInline = true;
    video.srcObject = mediaStream;

    await waitForVideoReady(video);
    await video.play();

    isCameraReady = true;
    captureStatus.textContent = "Cámara activa. Centre el rostro, use buena iluminación y capture el fotograma.";
    updateControls();
  } catch (error) {
    stopCamera();
    captureStatus.textContent = `Error: ${error.message}`;
    updateControls();
  }
}

/**
 * Captura un fotograma desde el video activo y lo convierte a imagen JPEG local.
 */
function captureFrame() {
  try {
    clearResult();

    if (!mediaStream || !video.srcObject) {
      throw new Error("La cámara no está activa.");
    }

    if (!isCameraReady || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
      throw new Error("El video aún no está listo. Espere un segundo e intente de nuevo.");
    }

    if (video.videoWidth === 0 || video.videoHeight === 0) {
      throw new Error("No fue posible obtener dimensiones válidas del video.");
    }

    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    liveImageDataUrl = canvas.toDataURL("image/jpeg", 0.95);

    if (!liveImageDataUrl || !liveImageDataUrl.startsWith("data:image/jpeg;base64,")) {
      throw new Error("No fue posible generar la imagen capturada.");
    }

    canvas.hidden = false;
    captureStatus.textContent = "Fotograma capturado correctamente.";
    updateControls();
  } catch (error) {
    liveImageDataUrl = null;
    captureStatus.textContent = `Error: ${error.message}`;
    updateControls();
  }
}

/**
 * Envía la imagen del documento y la captura facial al backend.
 */
async function verifyIdentity() {
  try {
    clearResult();

    if (!adultConsent.checked) {
      throw new Error("Debe declarar que es mayor de edad.");
    }

    if (!consent.checked) {
      throw new Error("Debe aceptar el consentimiento.");
    }

    if (documentImage.files.length !== 1) {
      throw new Error("Debe cargar exactamente una imagen del documento.");
    }

    if (!liveImageDataUrl) {
      throw new Error("Debe capturar un fotograma facial antes de verificar.");
    }

    result.textContent = "Procesando...";

    const documentDataUrl = await readFileAsDataUrl(documentImage.files[0]);

    const response = await fetch("/api/v1/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        consent_accepted: adultConsent.checked && consent.checked,
        document_image_b64: documentDataUrl,
        live_image_b64: liveImageDataUrl
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Error de verificación.");
    }

    setDecisionLabel(data.decision);
    result.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
  }
}

/**
 * Gestiona cambios de consentimiento.
 */
function handleLegalAcceptanceChange() {
  clearResult();

  const hasAdultDeclaration = adultConsent.checked;
  const hasConsent = consent.checked;

  if (!hasAdultDeclaration || !hasConsent) {
    stopCamera();
    clearLiveCapture();

    if (!hasAdultDeclaration) {
      captureStatus.textContent = "Debe declarar que es mayor de edad para activar la cámara.";
    } else {
      captureStatus.textContent = "Debe aceptar el consentimiento para activar la cámara.";
    }
  } else {
    captureStatus.textContent = "Declaración y consentimiento aceptados. Puede activar la cámara.";
  }

  updateControls();
}

/**
 * Gestiona cambios en la imagen del documento.
 */
function handleDocumentChange() {
  clearResult();
  updateControls();
}

adultConsent.addEventListener("change", handleLegalAcceptanceChange);
consent.addEventListener("change", handleLegalAcceptanceChange);
documentImage.addEventListener("change", handleDocumentChange);
startCameraButton.addEventListener("click", startCamera);
captureFrameButton.addEventListener("click", captureFrame);
verifyButton.addEventListener("click", verifyIdentity);

captureFrameButton.disabled = true;
canvas.hidden = true;
updateControls();
