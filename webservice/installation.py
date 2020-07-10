import os


import gidgethub.routing


router = gidgethub.routing.Router()


from gidgethub import apps


from webservice.constants import ROBOT_FEED_EVENTS_LABEL


@router.register("installation", action="created")
async def repo_installation_added(event, gh, *args, **kwargs):
    """ Create the #feed/events label in the repo where it gets installed """
    installation_id = event.data["installation"]["id"]
    installation_access_token = await apps.get_installation_access_token(
        gh,
        installation_id=installation_id,
        app_id=os.environ.get("GH_APP_ID"),
        private_key=os.environ.get("GH_PRIVATE_KEY"),
    )
    for repo in event.data["repositories"]:
        await handle_installed_repo_event(
            gh,
            installation_access_token,
            repo,
            installed_by=event.data["sender"]["login"],
        )


@router.register("installation_repositories", action="added")
async def repo_installation_added(event, gh, *args, **kwargs):
    """ Create the #feed/events label in the repo where it gets installed """
    installation_id = event.data["installation"]["id"]
    installation_access_token = await apps.get_installation_access_token(
        gh,
        installation_id=installation_id,
        app_id=os.environ.get("GH_APP_ID"),
        private_key=os.environ.get("GH_PRIVATE_KEY"),
    )
    for repo in event.data["repositories_added"]:
        await handle_installed_repo_event(
            gh,
            installation_access_token,
            repo,
            installed_by=event.data["sender"]["login"],
        )


async def handle_installed_repo_event(gh, access_token, repo, installed_by):
    repo_full_name = repo["full_name"]

    response = await gh.post(
        f"/repos/{repo_full_name}/labels",
        data={
            "name": ROBOT_FEED_EVENTS_LABEL,
            "description": "Automatically share this issue to PyLadies Slack #events channel",
        },
        oauth_token=access_token["token"],
    )
    label_url = response["url"]

    url = f"/repos/{repo_full_name}/issues"
    response = await gh.post(
        url,
        data={
            "title": "Thanks for installing the PyLadies GitHub App",
            "body": f"Thanks @{installed_by}! I've created the label **[[:robot: feed-events]({label_url})]** in this repository.",
        },
        oauth_token=access_token["token"],
    )
    issue_url = response["url"]
    await gh.patch(
        issue_url, data={"state": "closed"}, oauth_token=access_token["token"],
    )
