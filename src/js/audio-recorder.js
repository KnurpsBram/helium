var audioRecorder = {

    audioBlobs: [],
    mediaRecorder: null,
    streamBeingCaptured: null,

    start: function () {
        
        console.log("start recording audio...");

        return navigator.mediaDevices.getUserMedia({audio: true})
            .then(stream => {
                audioRecorder.streamBeingCaptured = stream;

                audioRecorder.mediaRecorder = new MediaRecorder(stream);

                audioRecorder.mediaRecorder.addEventListener('dataavailable', event => {
                    audioRecorder.audioBlobs.push(event.data);
                });

                audioRecorder.mediaRecorder.start();
            });
    },

    stop: function () {
        
        console.log("stop recording audio...");

        let mimeType = audioRecorder.mediaRecorder.mimeType;
        console.log(mimeType);

        return new Promise(resolve => {
            audioRecorder.mediaRecorder.addEventListener("stop", () => {

                let audioBlob = new Blob(audioRecorder.audioBlobs, {type: mimeType});

                resolve(audioBlob);
            });
        
            audioRecorder.mediaRecorder.stop();
            audioRecorder.streamBeingCaptured.getTracks().forEach(track => track.stop());
        
        });
    },

    reset: function () {
        audioRecorder.audioBlobs = [];
        audioRecorder.mediaRecorder = null;
        audioRecorder.streamBeingCaptured = null;
    }
}
