string_format = "{sentence} {sensors}"
xml_body_format = "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xml:lang=\"en-US\">{content}</speak>"
xml_voice_format = "<voice name=\"{name}\">{content}</voice>"
xml_break_format = "<break time=\"{time}\" />"
voices = {
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural"
}


entity_id = data.get("entity_id")
translations = data.get("translations")
sensors = data.get("sensors")
alternative = data.get("alternative")
delay = data.get("delay")


# Filter to get only active sensors
def filter_sensors(sensors):
    filtered_sensors = []

    for sensor in sensors:
        if hass.states.get(sensor['entity_id']).state == 'on':
            filtered_sensors.append(sensor)

    return filtered_sensors


# Generate the string of the concatinated names for the sensors based on a language
def build_sensor_string(sensors, language):
    strings = []

    for sensor in sensors:
        strings.append(sensor['translations'][language])

    return ", ".join(strings)


# Build the strings for all languages
def build_strings(sensors, translations):
    full_translations = translations

    for key, value in translations.items():
        sensor_string = build_sensor_string(sensors, key)
        full_translations[key] = string_format.format(
            sentence=value, sensors=sensor_string)

    return full_translations


# Replace 'Umlaute' with unicode
def unicode_replacer(text):
    text = text.replace('ä', '&#228;')
    text = text.replace('ö', '&#246;')
    text = text.replace('ü', '&#252;')
    text = text.replace('Ä', '&#196;')
    text = text.replace('Ö', '&#214;')
    text = text.replace('Ü', '&#220;')

    return text


# Build the SSML
def build_ssml(strings):
    first = True
    body = ""

    for key, value in strings.items():
        if first:
            first = False
            if delay is not None:
                value = xml_break_format.format(time=delay) + value

        body = body + \
            xml_voice_format.format(
                name=voices[key], content=unicode_replacer(value))

    return xml_body_format.format(content=body)


filtered_sensors = filter_sensors(sensors)

if len(filtered_sensors) > 0:
    hass.services.call("tts", "microsoft_ssml_say", {
        "entity_id": entity_id,
        "message": build_ssml(build_strings(filtered_sensors, translations))}, False)
elif alternative is not None:
    hass.services.call("tts", "microsoft_ssml_say", {
        "entity_id": entity_id,
        "message": build_ssml(alternative)}, False)
