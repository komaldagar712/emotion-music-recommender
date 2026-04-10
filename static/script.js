const video = document.getElementById('video');

// Start camera
navigator.mediaDevices.getUserMedia({
    video: true
})
.then(stream => {
    video.srcObject = stream;
});

// Capture image
function capture() {

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    const image = canvas.toDataURL('image/jpeg');

    fetch('/detect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: image })
    })
    .then(res => res.json())
    .then(data => {

        document.getElementById('emotion').innerText =
            "Your Emotion: " + data.emotion;

        const songList = document.getElementById('songs');
        songList.innerHTML = "";

        data.songs.forEach(song => {
            const li = document.createElement('li');
            li.innerText = "🎵 " + song;
            songList.appendChild(li);
        });

    });
}