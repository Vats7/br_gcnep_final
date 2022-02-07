console.log('chime')


const logger = new ChimeSDK.ConsoleLogger('ChimeMeetingLogs', ChimeSDK.LogLevel.INFO);
const deviceController = new ChimeSDK.DefaultDeviceController(logger);
const configuration = new ChimeSDK.MeetingSessionConfiguration(meeting, attendee);
const meetingSession = new ChimeSDK.DefaultMeetingSession(configuration, logger, deviceController);





