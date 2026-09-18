// Twilio Function /screen, Protected.
exports.handler = function(context,event,callback) {
  const r=new Twilio.twiml.VoiceResponse();
  if (event.Digits==='1') {r.say('Connecting your caller.');}
  else if (event.Digits) {r.hangup();}
  else {
    const g=r.gather({input:'dtmf',numDigits:1,timeout:5,action:`https://${context.DOMAIN_NAME}/screen`,method:'POST'});
    g.say('Business call. Press one to answer.');r.hangup();
  }
  callback(null,r);
};
