var startRecordingButton  = document.getElementsByClassName('start-recording-button')[0];
var stopRecordingButton   = document.getElementsByClassName('stop-recording-button')[0];
var audioPlayer           = document.getElementById("audio-player");
var deleteRecordingButton = document.getElementsByClassName('delete-recording-button')[0];
var startRecordingButtonContainer = document.getElementsByClassName('start-recording-button-container')[0];
var stopRecordingButtonContainer  = document.getElementsByClassName('stop-recording-button-container')[0];
var audioPlayerContainer          = document.getElementsByClassName("audio-player-container")[0];

function startAudioRecording() {
    audioRecorder.start();

    audioPlayerContainer.style.display          = "none";
    startRecordingButtonContainer.style.display = "none";
    stopRecordingButtonContainer.style.display  = "block";
}

function stopAudioRecording() { 
    audioRecorder.stop().then(audioBlob => {

        console.log("audioBlob", audioBlob);

        // file = blobToFile(audioBlob, "audio.wav");//.then(file => {
        // //});

        // let audioUrl = URL.createObjectURL(audioBlob);

        //going by example here: https://auphonic.com/help/api/examples.html
        let apiUrl = "http://127.0.0.1:5000/api";
        var xhr = new XMLHttpRequest();
        xhr.open("POST", apiUrl, true);

        var formData = new FormData();
        formData.append("file", audioBlob, "file");

        xhr.send(formData);
                
        // audioPlayer.src = audioUrl;
        // audioPlayer.load(); // this doesn't appear to be working
    });
    
    audioPlayerContainer.style.display          = "block";
    startRecordingButtonContainer.style.display = "none";
    stopRecordingButtonContainer.style.display  = "none";        
}

// // START TEMP
// //convert Blob to File. Pass the blob and the file title as arguments
// function blobToFile(theBlob, fileName) {
//     var file = new File([theBlob], fileName);
//     return file;
// }
// // END TEMP

function deleteRecording() {
    audioRecorder.reset();

    audioPlayerContainer.style.display          = "none";
    startRecordingButtonContainer.style.display = "block";
    stopRecordingButtonContainer.style.display  = "none";
}

startRecordingButton.onclick  = startAudioRecording;
stopRecordingButton.onclick   = stopAudioRecording;
deleteRecordingButton.onclick = deleteRecording;
