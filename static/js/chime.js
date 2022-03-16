console.log('chime')


const meetingUrl = window.location.href + "get_meeting"
const attendeeUrl = window.location.href + "get_attendee"


async function ajaxGetMeeting() {
    let response;

    try {
        response = await $.ajax({
            url: meetingUrl,
            type: 'GET',
            dataType:'json',
        });

        return response;
    } catch (error) {
        console.error(error);
    }
}

async function ajaxGetAttendee() {
    let response;

    try {
        response = await $.ajax({
            url: attendeeUrl,
            type: 'GET',
            dataType:'json',
        });

        return response;
    } catch (error) {
        console.error(error);
    }
}

// const meeting = {'MeetingId': '429daaf1-0429-47b1-a508-39c36bbe2713', 'ExternalMeetingId': '7cbea5eb-4bac-4611-9e2f-f3a48fc5bca0', 'MediaRegion': 'ap-south-1', 'MediaPlacement': {'AudioHostUrl': 'ff1852f1a846e9013b7581f656042123.k.m3.ao1.app.chime.aws:3478', 'AudioFallbackUrl': 'wss://haxrp.m3.ao1.app.chime.aws:443/calls/429daaf1-0429-47b1-a508-39c36bbe2713', 'SignalingUrl': 'wss://signal.m3.ao1.app.chime.aws/control/429daaf1-0429-47b1-a508-39c36bbe2713', 'TurnControlUrl': 'https://2713.cell.us-east-1.meetings.chime.aws/v2/turn_sessions', 'ScreenDataUrl': 'wss://bitpw.m3.ao1.app.chime.aws:443/v2/screen/429daaf1-0429-47b1-a508-39c36bbe2713', 'ScreenViewingUrl': 'wss://bitpw.m3.ao1.app.chime.aws:443/ws/connect?passcode=null&viewer_uuid=null&X-BitHub-Call-Id=429daaf1-0429-47b1-a508-39c36bbe2713', 'ScreenSharingUrl': 'wss://bitpw.m3.ao1.app.chime.aws:443/v2/screen/429daaf1-0429-47b1-a508-39c36bbe2713'}, 'MeetingFeatures': {'Audio': {'EchoReduction': 'AVAILABLE'}}}
// const attendee = {'ExternalUserId': 'd9604a70-4d1c-4ff9-9957-d10f1a9183cd', 'AttendeeId': '83d71e4e-49f0-ad1f-d8d3-d9bbb6e2cbd3', 'JoinToken': 'ODNkNzFlNGUtNDlmMC1hZDFmLWQ4ZDMtZDliYmI2ZTJjYmQzOjA0YmU1YmRkLTk2NzMtNDM0ZS04YTI2LThkMWE4MzllYjUxZQ'}

async function Meeting() {

    const logger = new ChimeSDK.ConsoleLogger('ChimeMeetingLogs', ChimeSDK.LogLevel.INFO);
    const deviceController = new ChimeSDK.DefaultDeviceController(logger);
    const meeting = await ajaxGetMeeting();
    const attendee = await ajaxGetAttendee();
    const configuration = new ChimeSDK.MeetingSessionConfiguration(meeting, attendee);
    const meetingSession = new ChimeSDK.DefaultMeetingSession(configuration, logger, deviceController);
    const audioVideo = meetingSession.audioVideo;
    let audioInputDevices = null;
    let videoInputDevices = null;
    let audioOutputDevices = null;

    audioVideo.setDeviceLabelTrigger(async () =>
        await navigator.mediaDevices.getUserMedia({audio: true, video: true})
    );

    async function setup1() {
        audioInputDevices = await audioVideo.listAudioInputDevices();
        audioOutputDevices = await audioVideo.listAudioOutputDevices();
        videoInputDevices = await audioVideo.listVideoInputDevices();
    }

    await setup1();

    async function setup() {
        await audioVideo.chooseAudioInputDevice(audioInputDevices[0].deviceId);
        await audioVideo.chooseAudioOutputDevice(audioOutputDevices[0].deviceId);
        await audioVideo.chooseVideoInputDevice(videoInputDevices[0].deviceId);
    }

    await setup();

    const observer = {
        audioVideoDidStart: () => {
            audioVideo.startLocalVideoTile();
        },
        videoTileDidUpdate: tileState => {
            if (
                tileState.localTile ||
                !tileState.tileId  /*||          tileId === tileState.tileId*/
            ) {
                audioVideo.bindVideoElement(tileState.tileId, document.getElementById(tileState.tileId));
                return;
            }
            audioVideo.bindVideoElement(tileState.tileId, document.getElementById(tileState.tileId));
        }
    }
    audioVideo.addObserver(observer);
    audioVideo.start();
}


window.onload = async function () {
    await Meeting()
}