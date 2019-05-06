# Google Calendar API Test

Practicing and messing around with Google's Calendar API in Python. Currently all it does is list the events on all of your calendars for the current date, including start and end time.

## Getting Started

### Prerequisites
* Python (I used 3.7 for this)
* Carious API and credential thingos. See [here](https://developers.google.com/calendar/overview).
* Various packages. Can be installed via pip: `
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

## Authors

* Me

## Todo

* Add option to ignore calendar names, and simply print out all events for all calendars one after the other, in order.

* Allow choice of various time frames. e.g., events for today, tomorrow, the week, next week, etc.

* Probably something else. I'll think of it.

## Acknowledgments

* Google. And their quickstart for the Calendar API for Python. See [here](https://developers.google.com/calendar/quickstart/python).

## Changelog
### 06-05-2019
* Group and print events by date instead of by calendar ID.

### 03-05-2019
* Initial commit.