
class Notification(object):
    def invoke( self,
                product,
                product_group,
                product_price,
                invoked_rule=None): pass

class NotificationManager(object):
    def __init__(self):
        self.hooks = []

    def add_hook(self, notify):
        if (not hasattr(notify, 'invoke') or
            not notify.invoke.__class__.__name__ == 'function'):
            raise AttributeError("notify object must have an 'invoke' function "
                                 "attached to it")
    
        self.hooks.append(notify)

    def send_notification(self): pass
