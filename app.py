from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from corona_data import get_data_for_state

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    msg = request.form.get('Body')
    
    states = ['Andhra Pradesh', 'Bihar', 'Chhattisgarh', 'Delhi', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Odisha', 'Puducherry', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telengana', 'Chandigarh', 'Jammu and Kashmir', 'Ladakh', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']

    # Create reply
    resp = MessagingResponse()
    
    print(msg)
    if any([ s.lower()  in  msg.lower() for s in states]):
#    if msg in states:
        msg = get_data_for_state(msg)
    else:
        msg = get_data_for_state(states)
    
    for m in msg:
        resp.message(m)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)