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

recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
deleteButton.addEventListener("click", deleteRecording);

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

function stopRecording() {
    console.log("stopButton clicked");

    // disable the stop button
    stopButton.disabled = true;

    recordButtonContainer.style.display = "none";
    stopButtonContainer.style.display   = "none";      

    console.log(rec);

    // tell the recorder to stop the recording
    rec.stop();

    // stop microphone access
    gumStream.getAudioTracks()[0].stop();

    // create the wav blob and pass it to a callback function
    rec.exportWAV(buildAudioPlayer);

    audioPlayerContainer.style.display = "block";
    
}

function buildAudioPlayer(audioBlob) {
    console.log("building audioPlayer...");

    let audioUrl = URL.createObjectURL(audioBlob);

    // The flask app should be running on this ip (localhost)
    let apiUrl = "http://127.0.0.1:5000/api";

    var xhr = new XMLHttpRequest();
    let formData = new FormData();
    formData.append("file", audioBlob, "file");
    formData.append("audio_data", audioBlob);

    xhr.open("POST", apiUrl, true);
    xhr.send(formData);

    // FIXME: the block below does not work
    // It is supposed to receive a new audio file from the flask app
    // and put it into an audio player
    fetch(
        apiUrl, {
            method: "POST",
            cache: "no-cache",
            mode: "no-cors",
            body: formData
        }
    )
    .then(resp => {
        console.log(resp);
        console.log(resp.arrayBuffer());
        audioPlayer.src = URL.createObjectURL(new Blob([resp.arrayBuffer() ]))
        // audioPlayer.src = apiUrl;
    })

    // // The block below displays the recorded audio (without sending it to the flask app)
    // audioPlayer.controls = true;
    // audioPlayer.src = audioUrl;
}

function deleteRecording() {
    console.log("deleteButton clicked");

    recordButton.disabled = false;

    audioPlayerContainer.style.display  = "none";
    recordButtonContainer.style.display = "block";
    stopButtonContainer.style.display   = "none";
}
