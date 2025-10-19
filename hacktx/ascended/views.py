from django.shortcuts import render
from allauth.socialaccount.models import SocialAccount, SocialToken
import google.oauth2.credentials
from googleapiclient.discovery import build
import datetime

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        try:
            soc_acc = SocialAccount.objects.get(user=request.user, provider="google")
            token = SocialToken.objects.get(account=soc_acc)
        except (SocialAccount.DoesNotExist, SocialToken.DoesNotExist):
            return render(request, 'ascended/index.html', {
                'error': 'Google login failed'
            })
        
        access_token = token.token
        refresh_token = token.token_secret

        client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
        client_secret = settings.SOCIAL_AUTH_GOOGLE_SECRET

        creds = google.oauth2.credentials.Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        )

        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        events = []
        page_token = None

        cur_time = datetime.datetime.utcnow().isoformat() + 'Z' # Z used to indicate UTC time
        end_time = (datetime.datetime.utcnow() + datetime.timedelta(days=10)).isoformat() + "Z"

        events_res = service.events().list(
            calendarId="primary",
            timeMin=cur_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_res.get('items', [])
        print(events)

    return render(request, 'ascended/index.html')