import os


import gidgethub.routing

from gidgethub import apps


router = gidgethub.routing.Router()
from slack import WebClient
from slack.errors import SlackApiError


from webservice.constants import ROBOT_FEED_EVENTS_LABEL


@router.register("issues", action="labeled")
async def issue_labeled(event, gh, *args, **kwargs):
    for label in event.data["issue"]["labels"]:
        if label["name"] == ROBOT_FEED_EVENTS_LABEL:
            issue_title = event.data["issue"]["title"]
            issue_body = event.data["issue"]["body"]
            html_url = event.data["issue"]["html_url"]

            # post it to Slack "events" channel
            slack_client = WebClient(token=os.getenv("SLACK_API_KEY"))
            try:
                response = slack_client.chat_postMessage(
                    channel="#events",
                    text=f"*New Event posted*\n\n*Title*: {issue_title}\n{issue_body}\n\n_source:_ _{html_url}_ ",
                )
            except SlackApiError as e:
                # You will get a SlackApiError if "ok" is False
                assert e.response["ok"] is False
                assert e.response[
                    "error"
                ]  # str like 'invalid_auth', 'channel_not_found'

            installation_id = event.data["installation"]["id"]
            installation_access_token = await apps.get_installation_access_token(
                gh,
                installation_id=installation_id,
                app_id=os.environ.get("GH_APP_ID"),
                private_key=os.environ.get("GH_PRIVATE_KEY"),
            )

            response = await gh.post(
                event.data["issue"]["comments_url"],
                data={
                    "body": "Thanks for sharing this event with PyLadies!! We've shared this in PyLadies Slack #events channel."
                },
                oauth_token=installation_access_token["token"],
            )
