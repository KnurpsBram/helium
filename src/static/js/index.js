var gumStream; // stream from getUserMedia()
var rec;       // Recorder.js object
var input;     // MediaStreamAudioSourceNode we'll be recording

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext
    
var audioPlayer           = document.getElementById("audio-player");
var audioPlayerContainer  = document.getElementById("audio-player-container");
var recordButton          = document.getElementsByClassName('record-button')[0];
var stopButton            = document.getElementsByClassName('stop-button')[0];
var deleteButton          = document.getElementsByClassName('delete-button')[0];
var recordButtonContainer = document.getElementById("record-button-container");
var stopButtonContainer   = document.getElementById('stop-button-container');

// The flask app should be running on this ip (localhost)
// var apiUrl = "http://127.0.0.1:5000/api";
// var apiUrl = "https://192.168.178.16:5000/api";
// var apiUrl = "https://192.168.178.128:5000/api";
var apiUrl = "https://80.112.116.8:5000/api";


recordButton.addEventListener("click", startRecording);
function startRecording() {

    console.log("recordButton clicked");

    // Simple constraints object, for more advanced audio features see
    // https://addpipe.com/blog/audio-constraints-getusermedia/
    var constraints = { audio: true, video: false }

    // Disable the record button until we get a success or fail from getUserMedia() 
    recordButton.disabled = true;
    stopButton.disabled = false;

    recordButtonContainer.style.display = "none"; // display type 'none' means "no, don't show this bit"
    stopButtonContainer.style.display = "block";  // display type 'block' means "yes, show this bit"
    
    // We're using the standard promise based getUserMedia() 
    // https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia 
    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        // create an audio context after getUserMedia is called
        // the sampleRate defaults to the one set in your OS for your playback device
        audioContext = new AudioContext();

        // assign to gumStream for later use
        gumStream = stream;

        input = audioContext.createMediaStreamSource(stream);
        rec = new Recorder(input,{numChannels:1})
        rec.record()

        console.log("Recording started");
    }).catch(function(err) {
        // enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
    });
}


stopButton.addEventListener("click", stopRecording);
function stopRecording() {

    console.log("stopButton clicked");

    // disable the stop button
    stopButton.disabled = true;

    recordButtonContainer.style.display = "none";
    stopButtonContainer.style.display   = "none";      

    // tell the recorder to stop the recording
    rec.stop();

    // stop microphone access
    gumStream.getAudioTracks()[0].stop();

    // create the wav blob and pass it to a callback function
    rec.exportWAV(buildAudioPlayer);

    // show the audio player
    audioPlayerContainer.style.display = "block";
}

function buildAudioPlayer(audioBlob) {

    console.log("building audioPlayer...");

    audioUrl = URL.createObjectURL(audioBlob);

    var xhr = new XMLHttpRequest();
    let formData = new FormData();
    formData.append("file", audioBlob, "file");
    formData.append("audio_data", audioBlob);
    formData.append("formant_multiplier", calculateFormantMultiplier());
    formData.append("pitch_multiplier", calculatePitchMultiplier());
    formData.append("tempo_multiplier", calculateTempoMultiplier());

    xhr.open("POST", apiUrl, false);

    fetch(
        apiUrl, {
            method: 'POST',
            body: formData
        }
    )
    .then(resp => {
        if (resp.ok) {
            resp.arrayBuffer().then(function(buffer) {
                var new_blob = new Blob([buffer], {type: 'audio/wav'});
        
                audioUrl = URL.createObjectURL(new_blob);
    
                audioPlayer.src = audioUrl;
            });
        } else {
            alert("something is wrong")
        }
    })
}


deleteButton.addEventListener("click", deleteRecording);
function deleteRecording() {
    console.log("deleteButton clicked");

    recordButton.disabled = false;

    audioPlayerContainer.style.display  = "none";
    recordButtonContainer.style.display = "block";
    stopButtonContainer.style.display   = "none";
}


var formantSlider = document.getElementById("formantSlider");
var pitchSlider = document.getElementById("pitchSlider");
var tempoSlider = document.getElementById("tempoSlider");

var formantText = document.getElementById("formantText");
var pitchText = document.getElementById("pitchText");
var tempoText = document.getElementById("tempoText");

formantSlider.addEventListener("input", setFormantText);
pitchSlider.addEventListener("input", setPitchText);
tempoSlider.addEventListener("input", setTempoText);

setFormantText();
setPitchText();
setTempoText();

function setFormantText() {
    formantText.innerHTML = calculateFormantMultiplier();
};

function setPitchText() {
    pitchText.innerHTML = calculatePitchMultiplier();
};

function setTempoText() {
    tempoText.innerHTML = calculateTempoMultiplier();
};

function calculateFormantMultiplier() {
    return Math.pow(10, formantSlider.value / 100).toFixed(2);
}

function calculatePitchMultiplier() {
    return Math.pow(10, pitchSlider.value / 100).toFixed(2);
}

function calculateTempoMultiplier() {
    return Math.pow(10, tempoSlider.value / 100).toFixed(2);
}
