from flask import Flask, send_file, render_template_string, Response, send_from_directory
from flask_cors import CORS

import sys
sys.path.append('../FileLoader/')

from FileLoader import importFiles



app = Flask(__name__)
CORS(app)

ROOT_VIDEO_DIR = "/home/niklas/Videos"

VIDEO_DIRECTORY = ROOT_VIDEO_DIR

(videoList,videoMap,subsMap) = importFiles(ROOT_VIDEO_DIR)

sortedVideos = sorted(videoList)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("/home/niklas/Pictures/Screenshots","Screenshot from 2023-02-24 11-03-53.png")

@app.route('/subtitle/<subfilename>')
def stream_subtitles(subfilename):
    print("SUBTITLES")
    subtitles = []
    try:
        subtitles = subsMap[subfilename]
    except:
        return b'',404

    if len(subtitles) == 0:
        return b'',404
    else:
        english = '_eng.vtt'
        print(subtitles)
        lambdaMatch = lambda x : x if english in x[1] else None
        lambdaFilter = lambda x : True if x is not None else False
        reduced = list(filter(lambdaFilter,list(map(lambdaMatch,subtitles))))

        print(reduced)

        (path,file) = reduced[0]
        print(reduced[0])
    return send_from_directory(path,file)


@app.route('/video/<filename>')
def stream_video(filename):
    (path,file) = videoMap[filename]
    return send_from_directory(path,file)

@app.route('/')
def index():
    videos = sortedVideos
    subtitles = subsMap
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <link href="https://vjs.zencdn.net/8.16.1/video-js.css" rel="stylesheet" />
    <title>Video Streaming with Subtitles</title>
    <link href="https://vjs.zencdn.net/7.20.3/video-js.min.css" rel="stylesheet">
    <script src="https://vjs.zencdn.net/7.20.3/video.min.js"></script>
    <script src="https://www.gstatic.com/cv/js/sender/v1/cast_sender.js?loadCastFramework=1"></script>
    <script src="https://cdn.jsdelivr.net/npm/vtt.js"></script>
    <script>
        var player;
        let subtitles = [];
        let currentSubtitleIndex = 0;
        let subtitleDiv;


        window['__onGCastApiAvailable'] = function(isAvailable) {
            if (isAvailable) {
                initializeCastApi();
            }
        };

        function initializeCastApi() {
            cast.framework.CastContext.getInstance().setOptions({
                receiverApplicationId: chrome.cast.media.DEFAULT_MEDIA_RECEIVER_APP_ID,
                autoJoinPolicy: chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED
            });
        }

        function initializePlayer() {
            player = videojs('videoPlayer', {
                controls: true,
                autoplay: false,
                preload: 'auto',
                playbackRates: [0.5, 1, 1.5, 2]
            });

            // Add event listener for play/pause button
            player.on('play', function() {
                updatePlayPauseButton();
            });
            player.on('pause', function() {
                updatePlayPauseButton();
            });
        }

        function updatePlayPauseButton() {
            var playPauseButton = player.getChild('controlBar').getChild('playToggle');
            if (player.paused()) {
                playPauseButton.el().classList.remove('vjs-playing');
                playPauseButton.el().classList.add('vjs-paused');
            } else {
                playPauseButton.el().classList.remove('vjs-paused');
                playPauseButton.el().classList.add('vjs-playing');
            }
        }

        function loadVideo(videoSrc, subtitleSrc) {
            if (!player) {
                initializePlayer();
            }

            player.src({ type: 'video/mp4', src: videoSrc });
                       
            // Create a div for custom subtitles
            if (!subtitleDiv) {
                subtitleDiv = document.createElement('div');
                subtitleDiv.className = 'vjs-text-track-display';
                player.el().appendChild(subtitleDiv);
            }

            // Add new subtitle track if available
            fetch(subtitleSrc)
                .then(response => {
                    if (response.ok) {
                        return response.text();
                    } else {
                        throw new Error('Subtitle file not found');
                    }
                })
                .then(subtitleContent => {
                    currentSubtitleIndex = 0;

                    var track = player.addRemoteTextTrack({
                        kind: 'subtitles',
                        srclang: 'en',
                        label: 'English',
                        src: subtitleSrc,
                        mode : 'showing',
                        default: true
                    }, false);

                    // Extract and display subtitle metadata
                    var parser = new WebVTT.Parser(window, WebVTT.StringDecoder());
                    var cues = [];
                    parser.oncue = function(cue) {
                        cues.push(cue);
                    };
                    parser.onflush = function() {
                        console.log('Subtitle metadata:');
                        console.log('Number of cues:', cues.length);
                        if (cues.length > 0) {
                            console.log('First cue start time:', cues[0].startTime);
                            console.log('Last cue end time:', cues[cues.length - 1].endTime);
                        }
                    };
                    parser.parse(subtitleContent);
                    parser.flush();

                    console.log('Subtitle track added:', subtitleSrc);
                })
                .catch(error => {
                    console.error('Error loading subtitle file:', error);
                });

            player.ready(() => {
                player.play();
            });
        }

        function castVideo(videoSrc, subtitleSrc) {
            var castSession = cast.framework.CastContext.getInstance().getCurrentSession();
            if (castSession) {
                // Create media info for the video
                var mediaInfo = new chrome.cast.media.MediaInfo(videoSrc, 'video/mp4');
                
                // Set up metadata
                var metadata = new chrome.cast.media.GenericMediaMetadata();
                mediaInfo.metadata = metadata;
                
                // Configure subtitle styling
                var textTrackStyle = new chrome.cast.media.TextTrackStyle();
                textTrackStyle.backgroundColor = '#00000000';  // transparent background
                textTrackStyle.foregroundColor = '#FFFFFF';    // white text
                textTrackStyle.edgeType = chrome.cast.media.TextTrackEdgeType.DROP_SHADOW;
                textTrackStyle.fontScale = 1.0;
                textTrackStyle.fontFamily = 'Arial';
                
                // Fetch and add subtitle track
                fetch(subtitleSrc)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Subtitle file not found');
                        }
                        return response.text();
                    })
                    .then(subtitleContent => {
                        // Create track with proper configuration
                        var track = new chrome.cast.media.Track(1, // unique ID
                            chrome.cast.media.TrackType.TEXT);
                        track.trackContentId = subtitleSrc;
                        track.trackContentType = 'text/vtt';
                        track.subtype = chrome.cast.media.TextTrackType.SUBTITLES;
                        track.name = 'English Subtitles';
                        track.language = 'en-US';
                        track.customData = null;

                        // Add track to media info
                        mediaInfo.textTrackStyle = textTrackStyle;
                        mediaInfo.tracks = [track];

                        // Configure media info
                        mediaInfo.streamType = chrome.cast.media.StreamType.BUFFERED;
                        mediaInfo.textTrackStyle = textTrackStyle;

                        // Create load request with subtitle settings
                        var request = new chrome.cast.media.LoadRequest(mediaInfo);
                        request.currentTime = 0;
                        request.autoplay = true;

                        // Enable subtitles by default
                        request.activeTrackIds = [1];  // matches the track ID we set above

                        // Load the media with proper error handling
                        castSession.loadMedia(request)
                            .then(() => {
                                console.log('Cast succeeded with subtitles');
                                
                                // Double-check subtitle activation after a short delay
                                setTimeout(() => {
                                    var mediaSession = castSession.getMediaSession();
                                    if (mediaSession && !mediaSession.activeTrackIds?.includes(1)) {
                                        mediaSession.setActiveTrackIds([1]);
                                    }
                                }, 1000);
                            })
                            .catch(error => {
                                console.error('Cast error:', error);
                                // Attempt to cast without subtitles as fallback
                                mediaInfo.tracks = [];
                                request = new chrome.cast.media.LoadRequest(mediaInfo);
                                return castSession.loadMedia(request);
                            });
                    })
                    .catch(error => {
                        console.error('Error with subtitles:', error);
                        // Cast without subtitles if subtitle file is not found
                        mediaInfo.tracks = [];
                        var request = new chrome.cast.media.LoadRequest(mediaInfo);
                        castSession.loadMedia(request)
                            .then(() => console.log('Cast succeeded without subtitles'))
                            .catch(error => console.error('Cast failed:', error));
                    });
            } else {
                console.log('No cast session available');
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            initializePlayer();
        });
    </script>
</head>
<body>
    <video-js id="videoPlayer" class="vjs-default-skin vjs-big-play-centered" controls preload="auto" width="640" height="360">
    </video-js>
    <google-cast-launcher></google-cast-launcher>
    <h1>Available Videos</h1>
    <ul>
    {% for video in videos %}
        <li>
            <a href="#" onclick="loadVideo('/video/{{ video }}', '/subtitle/{{ video }}')">{{ video }}</a>
            <button onclick="castVideo('https://' + window.location.hostname + ':' + window.location.port + '/video/{{ video }}', 'https://' + window.location.hostname + ':' + window.location.port +'/subtitle/{{ video }}')">Cast</button>
        </li>
    {% endfor %}
    </ul>
</body>
</html>
    ''', videos=videos,subtitles=subtitles)

if __name__ == '__main__':
    app.run(host='192.168.0.163', port=5000, debug=True)


