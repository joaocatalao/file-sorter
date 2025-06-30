import logging

class UILogHandler(logging.Handler):
    """Logging handler that forwards records to a UI callback."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        msg = self.format(record)
        try:
            self.callback(msg)
        except Exception:
            pass
