// Twilio Function /message, Protected. Recording retention is configured separately.
exports.handler=function(context,event,callback) {
  const r=new Twilio.twiml.VoiceResponse();
  if(event.RecordingSid) {
    r.say('Your recorded message has been received. Appointment requests are pending review and are not confirmed bookings.');r.hangup();
  } else {
    r.say('Glen is unavailable. You may leave a recorded message after the tone. Include your name, callback number, and requested service. To avoid recording, hang up now and use the usual email contact.');
    r.pause({length:2});
    r.record({action:`https://${context.DOMAIN_NAME}/message`,method:'POST',maxLength:120,playBeep:true,finishOnKey:'#',timeout:5});
    r.say('No message was recorded. Goodbye.');r.hangup();
  }
  callback(null,r);
};
