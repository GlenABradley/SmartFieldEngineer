// Twilio Function /after-dial, Protected.
exports.handler = function(context,event,callback) {
  const r=new Twilio.twiml.VoiceResponse();
  if(event.DialCallStatus==='completed') {r.hangup();}
  else {r.redirect({method:'POST'},`https://${context.DOMAIN_NAME}/message`);}
  callback(null,r);
};
