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

var apiUrl = "http://127.0.0.1:5000/api";

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

    // Until I've found a better way, we'll convert the audio to a string
    // and send it as JSON to the API
    audioBlob.arrayBuffer().then(function(buffer) {

        var int16arr = new Int16Array(buffer); // interpret the bits in the audioblob as 16-bit integers (that's usually right)
        var int16str = int16arr.join(",");  // convert the array to a string

        // Sumbit a POST request with JSON data
        var xhr = new XMLHttpRequest();

        apiUrl = "http://127.0.0.1:5000/api";

        xhr.open("POST", apiUrl, false);
        p = fetch(apiUrl, {
            method: 'POST',
            // mode: "no-cors",
            // cache: "no-cache",
            headers: {
                // 'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "helium_factor": 1.5, 
                "samplerate": 44100, // TODO: would be nice if we could read the samplerate from the blob somehow
                "audio": int16str
            })
        })
        .then(resp => {
            if (resp.ok) {
                return resp.json()
            } else {
                alert("something is wrong")
            }
        })
        .then(json => {
            console.log(json);

            // I can receive a string from flask
            // How to convert it to audio and play it as a blob?

            audioPlayer.src = audioUrl;
            audioPlayer.controls = true;

            audioPlayerContainer.style.display = "block";
        });
    });
}

function deleteRecording() {
    console.log("deleteButton clicked");

    recordButton.disabled = false;

    audioPlayerContainer.style.display  = "none";
    recordButtonContainer.style.display = "block";
    stopButtonContainer.style.display   = "none";
}
