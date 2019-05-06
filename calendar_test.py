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

# Quicksort algorithm
def quicksort(A, start, end):
	# Check to see if sorting is necessary
	if start < end:
		# Begin the quicksort
		pivot = partition(A, start, end)
		quicksort(A, start, pivot - 1)
		quicksort(A, pivot + 1, end)

# Bulk of the algorithm
def partition(A, start, end):
	pivot = A[start][1]
	l = start + 1
	r = end
	# Continue until the right side is done
	while True:
		while l <= r and A[l][1] <= pivot:
			l += 1
		while A[r][1] >= pivot and r >= l:
			r -= 1
		if r < l:
			break
		# Swap the two elements
		else:
			temp = A[l]
			A[l] = A[r]
			A[r] = temp
	# Make the final swap
	temp = A[start]
	A[start] = A[r]
	A[r] = temp
	# Return the new pivot
	return r

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

	# Get calendar ids and stick them into a dictionary
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
	tomorrow = (now + datetime.timedelta(days=7)).replace(hour=0,minute=0,second=0,microsecond=0)
	# Create events list
	events_list = []

	# Grab next 10 events for each calendar
	for key in calendar_ids:
		# Call the calendar api
		# Query to get events - calendar id, starting from now, 10 results, order by start time
		event_result = service.events().list(calendarId=calendar_ids[key], timeMin=now.isoformat() + localoffset, 
			timeMax=tomorrow.isoformat() + localoffset, maxResults=10, singleEvents=True, orderBy='startTime').execute()
		
		# Get list of events from events_result
		events = event_result.get('items', [])
		if not events:
			continue

		for event in events:
			# Get the start and end date and time (if it exists) of the event
			try:
				# Convert the returned strings to a datetime object
				start = datetime.datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
				end = datetime.datetime.strptime(event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
				# Stick the event into the list of events
				events_list.append([event['summary'], start, end])
			except:
				start = datetime.datetime.strptime(event['start']['date'] + localoffset, '%Y-%m-%d%z')
				end = datetime.datetime.strptime(event['end']['date'] + localoffset, '%Y-%m-%d%z')
				# Stick the event into the list of events
				events_list.append([event['summary'], start, end])

	# Quicksort the list of events
	quicksort(events_list, 0, len(events_list) - 1)

	# Grouped (by date) list of events
	grouped_events = []

	# Group events by date
	for item in events_list:
		item_date = datetime.datetime(year=item[1].year, month=item[1].month, day=item[1].day)
		# Check if grouped_events is greater than 0
		if len(grouped_events) < 1:
			# Append date and item if grouped_events is empty
			grouped_events.append([item_date, [item]])
		else:
			# Check if the current item's date exists in grouped_events
			date_exists = False
			for day in grouped_events:
				if day[0] == item_date:
					# Add the event to the day
					day[1].append(item)
					date_exists = True
					break
			# Add the date and the event if the date isn't in the grouped list
			if not date_exists:
				grouped_events.append([item_date, [item]])

	# Format the times and print the events
	for item in grouped_events:
		print("==" + item[0].strftime('%a %d/%m/%Y') + "==")
		for event in item[1]:
			try:
				# Format these datetime objects into the required format
				if (event[1].year == event[2].year) and (event[1].month == event[2].month) and (event[1].day == event[2].day):
					event[1] = event[1].strftime('%I:%M%p')
					event[2] = event[2].strftime('%I:%M%p')
				else:
					event[1] = event[1].strftime('%I:%M%p')
					event[2] = event[2].strftime('%I:%M%p - %d/%m/%Y')
			except:
				if (event[1].year != event[2].year) or (event[1].month != event[2].month) or (event[1].day != event[2].day):
					event[1] = ""
					event[2] = event[2].strftime('%d/%m/%Y')
				else:
					event[1] = ""
					event[2] = ""

			print(event[1] + " -> " + event[2] + "\n" + event[0] + "\n")

if __name__ == '__main__':
	main()