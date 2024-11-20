from posthog import Posthog

posthog = Posthog(
    project_api_key="phc_oUHMgNIxm78S6b6nVIW3k88CBkaHojf4UjXLUrJ6YkS",
    host="https://us.i.posthog.com",
)


def generic_posthog_event(event_name: str):
    posthog.capture("goodreads_bot_reloaded", event_name)
