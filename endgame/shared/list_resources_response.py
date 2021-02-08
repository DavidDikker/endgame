"""
When we list resources under a service, instead of returning an ARN or a name, return this object that collects both
and other metadata. Gives us more flexibility.
"""


class ListResourcesResponse:
    def __init__(self, service: str, arn: str, name: str, resource_type: str, account_id: str, region: str, note: str = None):
        self.service = service
        self.arn = arn
        self.name = name
        self.note = note
        self.account_id = account_id
        self.region = region
        self.resource_type = resource_type
