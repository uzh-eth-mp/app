

class KafkaManagerError(Exception):
    """Class for KafkaManager related errors"""
    pass


class KafkaManagerTimeoutError(KafkaManagerError):
    """Raised when a message is not retrieved from a topic for a some time."""
    pass
