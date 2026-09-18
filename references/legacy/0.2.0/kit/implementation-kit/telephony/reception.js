/* Twilio Function /reception, Protected visibility. No secrets in source.
   Environment: GLEN_NUMBER (E.164), BUSINESS_NAME, optional DND=true.
   Assign inbound voice webhook to this Function. Runtime supplies Twilio. */
exports.handler = function(context, event, callback) {
  const response = new Twilio.twiml.VoiceResponse();
  const base = `https://${context.DOMAIN_NAME}`;
  const speech = String(event.SpeechResult || '').toLowerCase();
  const digit = String(event.Digits || '');
  const wantsGlen = digit === '0' || /\b(glen|human|person|operator|connect|transfer)\b/.test(speech);
  const wantsMessage = digit === '1' || /\b(message|voicemail|callback|schedule|appointment|book)\b/.test(speech);
  if (!/^\+[1-9]\d{7,14}$/.test(context.GLEN_NUMBER || '')) {
    response.say('The office telephone is temporarily unavailable. Please try again later.');
    response.hangup(); return callback(null, response);
  }
  if (wantsGlen && context.DND !== 'true') {
    response.say('Connecting.');
    const dial = response.dial({action:base+'/after-dial', method:'POST',timeout:20,answerOnBridge:true});
    // Callee must press 1 so personal carrier voicemail cannot consume the call.
    dial.number({url:base+'/screen',method:'POST'},context.GLEN_NUMBER);
  } else if (wantsMessage || (wantsGlen && context.DND === 'true')) {
    response.redirect({method:'POST'},base+'/message');
  } else {
    const gather = response.gather({input:'speech dtmf',numDigits:1,action:base+'/reception',method:'POST',speechTimeout:'auto',timeout:5});
    gather.say(`${context.BUSINESS_NAME || 'Glen’s office'}. This is the automated receptionist. Say Glen or press zero to connect. To leave a message or request an appointment, say message or press one.`);
    response.redirect({method:'POST'},base+'/message');
  }
  callback(null,response);
};
