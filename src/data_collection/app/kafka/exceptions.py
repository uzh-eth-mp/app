

class KafkaManagerError(Exception):
    """Class for KafkaManager related errors"""
    pass


class KafkaConsumerTopicEmptyError(KafkaManagerError):
    """Raised when a message is not retrieved from a topic for a some time."""
    pass


class KafkaConsumerTimeoutError(KafkaManagerError):
    """Raised when a TimeoutError happens during consuming transactions.

    Note:
        This exception is not raised when simply waiting for new topic events.
    """