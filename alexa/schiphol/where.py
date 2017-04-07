"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import boto3  
import json
import re
import string
import math
from dateutil import parser
from datetime import timedelta, tzinfo, datetime
import random
import time
from collections import OrderedDict



# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {   
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Schiphol airport. How can I help you?"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Can I help you with something? For example, finding your " + \
                    " gate, or recommending somewhere to pass the time."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Enjoy your stay at Schiphol airport."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- API calls ------------------

def request_route(location):
    request_json = json.dumps({"location":location});
    print("Calling lambda to get route with data:" + request_json)
    client = boto3.client('lambda')
    response = client.invoke(FunctionName='doh2016_getroute', InvocationType='RequestResponse', Payload=request_json)
    print("Got response:")
    print(response)
    route_data = response['Payload'].read()
    print(route_data)
    route = json.loads(route_data)
    print(route)
    return route

def request_flight_info(flight_number):
    request_json = json.dumps({"flight_number":flight_number.upper()});
    print("Calling lambda to get route with data:" + request_json)
    client = boto3.client('lambda')
    response = client.invoke(FunctionName='doh2016_getflight', InvocationType='RequestResponse', Payload=request_json)
    print("Got response:")
    print(response)
    payload = response['Payload'].read()
    data = json.loads(payload)
    print(data)
    return data

def request_security_check_time(security_check_number):
    request_json = json.dumps({"security_check_number":security_check_number});
    print("Calling lambda to get security check number with data:" + request_json)
    client = boto3.client('lambda')
    response = client.invoke(FunctionName='doh2016_securitychecks', InvocationType='RequestResponse', Payload=request_json)
    print("Got response:")
    print(response)
    payload = response['Payload'].read()
    data = json.loads(payload)
    print(data)
    return data

# --------------- Slots ------------------

def get_location_slot(intent, session, session_attributes):
    location = None

    # See if it's already in the session. If so, return that.
    if "LOCATION_KEY" in session.get('attributes', {}):
        location = session['attributes']['LOCATION_KEY']
        print("Found location " + location + " in session");

    # Get from slot.
    if location is None:
        print("Did not find location in session");
        if 'Location' in intent['slots'] and 'value' in intent['slots']['Location']:
            print("Found location: " + intent['slots']['Location']['value'])
            location = intent['slots']['Location']['value']
        elif 'GateLetter' in intent['slots'] and 'GateNumber' in intent['slots']:
            gate_letter = intent['slots']['GateLetter']['value']
            gate_letter = re.sub('['+string.punctuation+']', '', gate_letter)
            gate_number = str(intent['slots']['GateNumber']['value'])
            if len(gate_number) == 1:
                gate_number = "0" + gate_number
            print("Found gate letter: " + gate_letter + " and #" + gate_number)
            location = gate_letter + gate_number

    # Set in session.
    print("Setting location " + location + " in session");
    session_attributes["LOCATION_KEY"] = location;

    return location

def get_flight_number_slot(intent, session, session_attributes):
    flight_number = None

    # See if it's already in the session. If so, return that.
    if "FLIGHT_NUMBER_KEY" in session.get('attributes', {}):
        flight_number = session['attributes']['FLIGHT_NUMBER_KEY']
        print("Found flight number " + flight_number + " in session");
    
    if flight_number is None:
        if 'LetterOne' in intent['slots'] and 'LetterOne' in intent['slots'] and 'Number' in intent['slots']:
            letter1 = intent['slots']['LetterOne']['value']
            letter2 = intent['slots']['LetterTwo']['value']
            number = str(intent['slots']['Number']['value'])
            print("Got slots letter1: " + letter1 + " letter2: " + letter2 + " number: " + number)
            flight_number = letter1 + letter2 + number
            flight_number = re.sub('['+string.punctuation+']', '', flight_number)
    
    # Set in session.
    print("Setting flight number " + flight_number + " in session");
    session_attributes["FLIGHT_NUMBER_KEY"] = flight_number.upper();
    return flight_number

def get_name_slot(intent, session, session_attributes):
    name = None

    if "NAME_KEY" in session.get('attributes', {}):
        name = session['attributes']['NAME_KEY']
        print("Found name " + name + " in session");

    return name

def set_value_in_session(session, key, value):
    print("Setting " + key + " to " + value + " in session")
    attrs = session.get("attributes")
    if attrs is None:
        attrs = {}
        session["attributes"] = attrs
    attrs[key] = value

# --------------- Screen ------------------

def post_to_queue(event):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='command_queue', QueueOwnerAWSAccountId='820681454374')
    response = queue.send_message(MessageBody=json.dumps(event))
    print("Got response:")
    print(response)

def show_route(intent, session):
    """ Post a message on the SQS queue so we show the route on the screen.
    """
    session_attributes = {}

    location = get_location_slot(intent, session, session_attributes)

    if location:
        print("Posting to queue for destination")
        event = { 'destination' : location }
        post_to_queue(event)

def show_flight(intent, session):
    """ Post a message on the SQS queue so we show the flight number on the screen.
    """
    session_attributes = {}

    flight_number = get_flight_number_slot(intent, session, session_attributes)

    if flight_number:
        print("Posting to queue for flight_number")
        event = { 'flight_number' : flight_number.upper() }
        post_to_queue(event)
        
# --------------- Speaking ------------------

def say_route(intent, session):
    """ Say the beginning of the route.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""

    location = get_location_slot(intent, session, session_attributes)

    if location:
        route = request_route(location)
        directions = route['directions']
        directions_unique = list(OrderedDict.fromkeys(directions))
        directions_unique = [ x for x in directions_unique if "stay" not in x ]
        directions_unique = [ x for x in directions_unique if "U-turn" not in x ]
        directions_unique = directions_unique[1:4] 

        speech_output = "To go to " + location + ", " + \
                        ", ".join(directions_unique) + \
                        ". See the screen for more details."
    else:
        speech_output = "I'm not sure where you want to go."
        reprompt_text = ""
        print("Did not receive a valid location")
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def _minutes_security_check(route):
    print("Checking if the GIS route passes through security. Data:")
    print(route)
    check_number = None

    # The text "Security Check X" will be inside the feature['attributes']['text'] element.
    security_check_text = 'Security Check '
    for text in route['directions']:
        print("Checking text: ", text)
        if security_check_text in text:
            number_index = text.index(security_check_text) + len(security_check_text)
            check_number = text[number_index:number_index + 1]
            print("FOUND Passes through security check #", check_number)
            break

    minutes_waiting = 0
    if check_number is not None:
        extra_minutes = request_security_check_time(check_number)
        print("Extra minutes waiting: ", extra_minutes)
        minutes_waiting = minutes_waiting + extra_minutes
    
    return minutes_waiting

def say_time(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    location = get_location_slot(intent, session, session_attributes);

    if location:
        route = request_route(location)
        time = route['time']
        waiting_time = _minutes_security_check(route)
        time = time + waiting_time
        
        speech_output = location + " is approximately " + str(time) + " minutes away"

        if waiting_time > 0:
            speech_output = speech_output + ", including " + str(waiting_time) + " minutes of security lines."
    else:
        speech_output = "I'm not sure what you are asking. "
        print("Did not receive a valid location")
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def ask_flight_number(intent, session):
    """ Ask for the flight number
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    speech_output = "Let's see. What's your flight number?"
    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def _get_time_till_flight(flight_info):
    # Timezone hack
    ZERO = timedelta(0)

    class UTC(tzinfo):
      def utcoffset(self, dt):
        return ZERO
      def tzname(self, dt):
        return "UTC"
      def dst(self, dt):
        return ZERO

    utc = UTC()
    now = datetime.now(utc)
    print("now")
    print(now)

    boarding_time_str = flight_info['expectedTimeBoarding']
    print("Got boarding time: ", boarding_time_str)
    boarding_time = parser.parse(boarding_time_str)
    diff_boarding = boarding_time - now
    print("diff time:")
    print(diff_boarding)
    diff_minutes_boarding = (diff_boarding.days * 24 * 60) + (diff_boarding.seconds/60)

    closing_time_str = flight_info['expectedTimeGateClosing']
    print("Got closing time: ", closing_time_str)
    closing_time = parser.parse(closing_time_str)
    diff_closing = closing_time - now
    print("diff time:")
    print(diff_closing)
    diff_minutes_closing = (diff_closing.days * 24 * 60) + (diff_closing.seconds/60)

    times = {"diff_minutes_boarding" : diff_minutes_boarding, "diff_minutes_closing" : diff_minutes_closing}
    print(times)
    return times


def _get_recommendation(session_attributes):
    recommendations = ["expo", "Starbucks", "Albert heijn", "the body shop"]
    recommendation = random.choice(recommendations)
    session_attributes['RECOMMENDATION_KEY'] = recommendation
    return recommendation

def say_flight_info(intent, session):
    """ Using flight number, say what they can do.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    flight_number = get_flight_number_slot(intent, session, session_attributes)
    flight_info = request_flight_info(flight_number)

    # Set the gate in the location in the session
    gate = flight_info['gate']
    session_attributes['LOCATION_KEY'] = gate

    speech_output = ""

    name = get_name_slot(intent, session, session_attributes)
    if name is not None:
        speech_output = speech_output + "Hi " + name + ". "

    times = _get_time_till_flight(flight_info)
    time_till_boarding = times['diff_minutes_boarding']
    time_till_closing = times['diff_minutes_closing']
    if (time_till_boarding > 60):
        recommendation = _get_recommendation(session_attributes)
        num_hours = math.floor(time_till_boarding / 60)
        print("Time greater than 60 min, in hours: " + str(num_hours))
        speech_output = speech_output + "Your flight is at gate " + gate + \
                        ", but it looks like you've got more than " + str(int(num_hours)) + " hours until your flight." + \
                        " How about stopping by " + recommendation + " first?"
        reprompt_text = "Would you like to check out " + recommendation + "?"
    elif (time_till_closing < 0):
        # already closed
        print("Time less than 0 min")
        speech_output = "Unfortunately, your flight " + flight_number + " is already closed. Please go to the information desk."
        should_end_session = True
    elif (time_till_boarding < 0):
        print("Time less than 0 min")
        speech_output = "Your flight has already started boarding, and closes in " + str(time_till_closing) + \
                        " minutes. Please head to gate " + gate
        should_end_session = True
    else:
        print("Time less than 60 min")
        speech_output = speech_output + "You're flights boards in " + str(time_till_boarding) + " minutes at gate " + gate + \
                        ". Please head to gate " + gate
        should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_recommendation(intent, session):
    # Set recommendation as the desired location
    if "RECOMMENDATION_KEY" in session.get('attributes'):
        attrs = session.get("attributes")
        attrs['LOCATION_KEY'] = attrs['RECOMMENDATION_KEY'];
        attrs['RECOMMENDATION_KEY'] = None
    
    # If there was no recommendation, then just use last location.
    show_route(intent, session)
    return say_route(intent, session)

def say_no_thanks(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""
    speech_output = "OK."

    try:
        show_route(intent, session)
        return say_route(intent, session)
    except:
        return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_new_recommendation(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    recommendation = _get_recommendation(session_attributes)

    speech_output = "How about " + recommendation + "?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def start_barcode(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""

    # Poll the queue every second
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='alexa_queue', QueueOwnerAWSAccountId='820681454374')

    print("Polling queue")
    messages = queue.receive_messages(MessageAttributeNames=['flight_number', 'name'], WaitTimeSeconds=20)

    if len(messages) > 0:
        print("messages received!")
        message = messages[0]
        print(message.body)
        body = message.body
        body = json.loads(body)
        name = body['name']
        flight_number = body['flight_number']

        # set flight number and name in current session
        set_value_in_session(session, 'FLIGHT_NUMBER_KEY', flight_number)
        set_value_in_session(session, 'NAME_KEY', name)

        print("purging queue")
        queue.purge()

        show_flight(intent, session)
        return say_flight_info(intent, session)
    else:
        print("no message received")
        speech_output = "I did not see any barcode"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_thanks(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""

    speech_output = "No problem."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_abilities(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""

    speech_output = "Ask me where points of interest are, how long you it takes to get to your gate, or for flight information."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_helpfulness(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""

    speech_output = "Thanks Luis. Can you imagine if there were one of me every hundred meters? Statistics show that having an automated, " + \
                    " personal assistant can drastically increase airport efficiency."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WhereIntent":
        print("Got WhereIntent")
        show_route(intent, session)
        return say_route(intent, session)
    elif intent_name == "WhenIntent":
        print("Got WhenIntent")
        show_route(intent, session)
        return say_time(intent, session)
    elif intent_name == "FlightIntent":
        print("Got FlightIntent")
        return ask_flight_number(intent, session)
    elif intent_name == "FlightNumberIntent":
        print("Got FlightNumberIntent")
        show_flight(intent, session)
        return say_flight_info(intent, session)
    elif intent_name == "RecommendationIntent":
        print("Got RecommendationIntent")
        return say_recommendation(intent, session)
    elif intent_name == "NoThanksIntent":
        print("Got NoThanksIntent")
        return say_no_thanks(intent, session)
    elif intent_name == "RecommendIntent":
        print("Got RecommendIntent")
        return say_new_recommendation(intent, session)
    elif intent_name == "BarcodeIntent":
        print("Got BarcodeIntent")
        return start_barcode(intent, session)
    elif intent_name == "ThanksIntent":
        print("Got ThanksIntent")
        return say_thanks(intent, session)
    elif intent_name == "AbilitiesIntent":
        print("Got AbilitiesIntent")
        return say_abilities(intent, session)
    elif intent_name == "HelpfulIntent":
        print("Got HelpfulIntent")
        return say_helpfulness(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        print("Got help intent")
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        print("Got cancel intent")
        return handle_session_end_request()
    else:
        print("Got invalid intent")
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.097dfe33-7aa8-44cb-b264-c534caf7bb27"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
