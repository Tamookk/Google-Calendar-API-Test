# Imports
import datetime
import dateutil.tz
import pickle
import os.path
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If mondifying this, delete file 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Main function
def main():
	"""
	Shows basic usage of the Google Calendar API
	Prints the start and name of the next 10 events on the user's calendar.
	"""
	creds = None
	# The file token.pickle stores the user's access and refreshtokens, and is
	# created automatically when the authorisation flow completes for the first
	# time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server(port=8090) # Port required as error given for default (8080)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)

	# Get calendar ids and stick them into a dict
	calendar_ids = {}
	page_token = None
	while True:
  		calendar_list = service.calendarList().list(pageToken=page_token).execute()
  		for calendar_list_entry in calendar_list['items']:
  			calendar_ids[calendar_list_entry['summary']] = calendar_list_entry['id']
  		
  		page_token = calendar_list.get('nextPageToken')
  		if not page_token:
  			break

  	# Set up the time objects
  	# Get the timezone
	localtz = dateutil.tz.tzlocal()
	localoffset = localtz.utcoffset(datetime.datetime.now(localtz))
	localoffset = localoffset.total_seconds() / 3600

	if localoffset % 1 == 0.5:
		if localoffset > 0:
			localoffset = "+" + str(int(localoffset)) + ":30"
		else:
			localoffset = str(int(localoffset)) + ":30"
	elif localoffset % 1 == 0.75:
		if localoffset > 0:
			localoffset = "+" + str(int(localoffset)) + ":45"
		else:
			localoffset = str(int(localoffset)) + ":45"
	else:
		if localoffset > 0:
			localoffset = "+" + str(int(localoffset)) + ":00"
		else:
			localoffset = str(int(localoffset)) + ":00"

	# Get the current time
	now = datetime.datetime.now()
	# Get the date tomorrow
	tomorrow = (now + datetime.timedelta(days=2)).replace(hour=0,minute=0,second=0,microsecond=0)

	# Grab next 10 events for each calendar
	print("==Today's Events: " + now.strftime('%d/%m/%Y') + "==")
	for key in calendar_ids:
		# Call the calendar api
		# Query to get events - calendar id, starting from now, 10 results, order by start time
		event_result = service.events().list(calendarId=calendar_ids[key], timeMin=now.isoformat() + localoffset, 
			timeMax=tomorrow.isoformat() + localoffset, maxResults=10, singleEvents=True, orderBy='startTime').execute()
		
		# Get list of events from events_result
		events = event_result.get('items', [])
		if not events:
			continue

		print("\n--" + key + "---")
		for event in events:
			# Get the start and end date and time (if it exists) of the event
			try:
				# Convert the returned strings to a datetime object
				start = datetime.datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
				end = datetime.datetime.strptime(event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
				# Format these datetime objects into the required format
				if (start.year == end.year) and (start.month == end.month) and (start.day == end.day):
					time = start.strftime('%I:%M%p -> ') + end.strftime('%I:%M%p - %d/%m/%Y')
				else:
					time = start.strftime('%I:%M%p - %d/%m/%Y -> ') + end.strftime('%I:%M%p - %d/%m/%Y')
			except:
				start = datetime.datetime.strptime(event['start']['date'], '%Y-%m-%d')
				end = datetime.datetime.strptime(event['end']['date'], '%Y-%m-%d')
				if (start.year == end.year) and (start.month == end.month) and (start.day == end.day):
					time = start.strftime('%d/%m/%Y')
				else:
					time = start.strftime('%d/%m/%Y -> ') + end.strftime('%d/%m/%Y')
			# Print the event info
			print(time + "\n" + event['summary'])

if __name__ == '__main__':
	main()