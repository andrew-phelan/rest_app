from .enums import Status, Outcome, EventType


class Sport(object):

    def __init__(self, name, slug, active=True):
        self.name = name
        self.slug = slug
        self.active = True if active == 1 else False


class Event(object):

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.slug = kwargs.get('slug')
        self.active = True if kwargs.get('active') == 1 else False
        self.sport = kwargs.get('sport')
        self.actual_start = kwargs.get('actual_start')
        self.scheduled_start = kwargs.get('scheduled_start')
        self.status = str(Status(kwargs.get('status')))
        self.type = str(EventType(kwargs.get('type')))


class Selection(object):

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.active = True if kwargs.get('active') == 1 else False
        self.event = kwargs.get('event')
        self.price = kwargs.get('price', '00.00')
        self.outcome = str(Outcome(kwargs.get('outcome')))
