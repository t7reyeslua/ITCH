"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import logging
import random

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


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
    speech_output = "Welcome to Amsterdam. " + \
                    "Discover the city from a new perspective. Ask me what I can do. "
    speech_output = "Welcome to Amsterdam. What can I do for you?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Can I help you with something? " + \
                    "You can ask me for interesting places or things to do around here." + \
                    "For example, finding your way or recommending somewhere to pass the time."

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for visiting Amsterdam. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Slots ------------------

def get_location_slot(intent, session, session_attributes):
    location = None

    # See if it's already in the session. If so, return that.
    if "LOCATION_KEY" in session.get('attributes', {}):
        location = session['attributes']['LOCATION_KEY']
        print("Found location " + str(location) + " in session")

    # Get from slot.
    if location is None:
        print("Did not find location in session")
        print(intent.get('slots', {}))
        if 'Location' in intent.get('slots',{}) and 'value' in intent['slots']['Location']:
            print("Found location: " + intent['slots']['Location']['value'])
            location = intent['slots']['Location']['value']

    # Set in session.
    print("Setting location " + str(location) + " in session")
    session_attributes["LOCATION_KEY"] = location

    return location

def get_venue_type_slot(intent, session, session_attributes):
    venue_type = None

    # See if it's already in the session. If so, return that.
    if "VENUE_TYPE_KEY" in session.get('attributes', {}):
        venue_type = session['attributes']['VENUE_TYPE_KEY']
        print("Found venue_type " + str(venue_type)  + " in session")

    # Get from slot.
    if venue_type is None:
        print("Did not find venue_type in session")
        print(intent.get('slots', {}))
        if 'VenueType' in intent.get('slots',{}) and 'value' in intent['slots']['VenueType']:
            print("Found venue_type: " + intent['slots']['VenueType']['value'])
            venue_type = intent['slots']['VenueType']['value']

    # Set in session.
    print("Setting venue_type " + str(venue_type) + " in session")
    session_attributes["VENUE_TYPE_KEY"] = venue_type

    return venue_type

def get_action_slot(intent, session, session_attributes):
    action = None

    # See if it's already in the session. If so, return that.
    if "ACTION_KEY" in session.get('attributes', {}):
        action = session['attributes']['ACTION_KEY']
        print("Found action " + str(action) + " in session")

    # Get from slot.
    if action is None:
        print("Did not find action in session")
        print(intent.get('slots', {}))
        if 'Action' in intent.get('slots', {}) and 'value' in intent['slots']['Action']:
            print("Found action: " + intent['slots']['Action']['value'])
            action = intent['slots']['Action']['value']

    # Set in session.
    print("Setting action " + str(action) + " in session")
    session_attributes["ACTION_KEY"] = action

    return action


def get_name_slot(intent, session, session_attributes):
    name = None

    if "NAME_KEY" in session.get('attributes', {}):
        name = session['attributes']['NAME_KEY']
        print("Found name " + name + " in session")

    return name


def set_value_in_session(session, key, value):
    print("Setting " + key + " to " + value + " in session")
    attrs = session.get("attributes")
    if attrs is None:
        attrs = {}
        session["attributes"] = attrs
    attrs[key] = value


# --------------- Speaking ------------------

def say_thanks(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""

    speech_output = "No problem."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_no_thanks(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""
    speech_output = "OK."

    if session.get('attributes', {}).get('SUGGESTION_KEY', False) is True:
        speech_output = "Well, the top restaurants near your location are Restaurant Seven Seas and Los Pilones. They are both around 10 minutes away"
        should_end_session = False
    if session.get('attributes', {}).get('ANNE_KEY', False) is True:
        print(session.get('attributes', {}))
        session_attributes["ANNE_KEY"] = True
        speech_output = "On average, it will take you around 2 hours to get in. Would you like me to suggest you something else instead?"
        should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_abilities(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "You can ask me where points of interest are," + \
                    " how long it takes to get to some place," + \
                    " cool unknown places to visit," + \
                    " or even for a quick random fact about the city."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def say_helpfulness(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "Can you imagine if there was one of me in every bus or tram stop? " + \
                    "You have a captive audience of people who is momentarily idle but willing to move around. " + \
                    "I can promote an engaging spontaneous natural interaction and help locals and tourist explore " + \
                    " and discover the city in a new fascinating way."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handleTransportationIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "Transportation result. " + \
                    "Do you want to know anything else?"

    action = get_action_slot(intent, session, session.get('attributes', {}))
    location = get_location_slot(intent, session, session.get('attributes', {}))

    if session.get('attributes', {}).get('SUGGESTION_KEY', False):
        speech_output = "You can take bus 22 which will be here in 6 minutes. It will take 9 minutes to get till stop Prince Hendrikkade where you can find it. Do you want anything else?"
    if location is not None and 'house' in location:
        speech_output = "You can take bus 658 and then walk 150 meters to the end of the street heading north. However, you need an entrance ticket. Do you already have one?"
        session_attributes["ANNE_KEY"] = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handleWhereIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "Where intent result. " + \
                    "Do you want to know anything else?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handleWhenIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "When intent result. " + \
                    "Do you want to know anything else?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handleDistanceIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "Distance intent result. " + \
                    "Do you want to know anything else?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handleQuickFactIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    quickFacts = [
        ' there are over one thousand and growing startups here in Amsterdam ',
        ' there are around 847 thousand bicycles in the city. ',
        ' around 14 thousand bikes are fished from the canals every year. ',
        ' there is a new local brewery two blocks aways that opened just last month. ',
    ]
    quickFact = quickFacts[int(random.randrange(0, len(quickFacts)-1))]
    speech_output = "Did you know that %s " % quickFact + \
                    "Do you want to know anything else?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handleWeatherIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "Weather intent result. " + \
                    "Do you want to know anything else?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handleRecommendIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    action = get_action_slot(intent, session, session.get('attributes', {}))
    location = get_location_slot(intent, session, session.get('attributes', {}))
    if session.get('attributes', {}).get('SUGGESTION_KEY', False) and location is None:
        speech_output = 'Any type in particular?'
    elif session.get('attributes', {}).get('SEVEN_SEAS_KEY', False):
        speech_output = "Today there is the Jazz festival in the Nieuwe Markt. It is a 9 minute walk away from there. Can I help you with something else?"
    else:
        speech_output = "Recommend intent result. " + \
                    "Do you want to know anything else?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handleTellSomeoneSomethingIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = ""

    who = intent['slots'].get('Name', {}).get('value', 'Andres')
    what = intent['slots'].get('Action', {}).get('value', 'shut up')

    speech_output = "%s, %s" % (who, what)

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handleRecommendationIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    print(session.get('attributes', {}))
    if session.get('attributes', {}).get('ANNE_KEY', False) is True:
        session_attributes["ANNE_KEY"] = True
        speech_output = "You can go to the open street market in kerkstraat. You would need to take bus 755 from here "
        should_end_session = False
    else:
        speech_output = "Recommendation intent result. " + \
                    "Do you want to know anything else?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handleSuggestIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "Anything in particular?"
    session_attributes["SUGGESTION_KEY"] = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handleSevenSeasIntent(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    speech_output = "You can take bus 22 which will be here in 6 minutes. It will take 9 minutes to get till stop Prince Hendrikkade where you can find it. Do you want anything else?"
    session_attributes["SEVEN_SEAS_KEY"] = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handleBenefitsIntent(intent, session):
    return say_helpfulness(intent, session)



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
          ", sessionId=" + session['sessionId'] +
          ", intent=" + intent_request['intent']['name'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "TransportationIntent":
        print("Got TransportationIntent")
        return handleTransportationIntent(intent, session)
    elif intent_name == "RecommendIntent":
        print("Got RecommendIntent")
        return handleRecommendIntent(intent, session)
    elif intent_name == "RecommendationIntent":
        print("Got RecommendationIntent")
        return handleRecommendationIntent(intent, session)
    elif intent_name == "WhereIntent":
        print("Got WhereIntent")
        return handleWhereIntent(intent, session)
    elif intent_name == "DistanceIntent":
        print("Got DistanceIntent")
        return handleDistanceIntent(intent, session)
    elif intent_name == "QuickFactIntent":
        print("Got QuickFactIntent")
        return handleQuickFactIntent(intent, session)
    elif intent_name == "WeatherIntent":
        print("Got WeatherIntent")
        return handleWeatherIntent(intent, session)
    elif intent_name == "BenefitsIntent":
        print("Got BenefitsIntent")
        return handleBenefitsIntent(intent, session)
    elif intent_name == "TellSomeoneSomethingIntent":
        print("Got TellSomeoneSomethingIntent")
        return handleTellSomeoneSomethingIntent(intent, session)
    elif intent_name == "ThanksIntent":
        print("Got ThanksIntent")
        return say_thanks(intent, session)
    elif intent_name == "SuggestIntent":
        print("Got SuggestIntent")
        return handleSuggestIntent(intent, session)
    elif intent_name == "SevenSeasIntent":
        print("Got SevenSeasIntent")
        return handleSevenSeasIntent(intent, session)
    elif intent_name == "NoThanksIntent":
        print("Got NoThanksIntent")
        return say_no_thanks(intent, session)
    elif intent_name == "AbilitiesIntent":
        print("Got AbilitiesIntent")
        return say_abilities(intent, session)
    elif intent_name == "HelpfulIntent":
        print("Got HelpfulIntent")
        return say_helpfulness(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
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
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    appId = event['session']['application']['applicationId']
    devId = event['context']['System'].get('device', {}).get('deviceId', None)
    logger.debug('Request coming from app %s and device %s' % (str(appId), str(devId)))

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
