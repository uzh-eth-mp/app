from enum import StrEnum, auto


class ProducerType(StrEnum):
    """The producer type."""

    FULL = auto()
    """FULL producer will go through every block and produce every transaction in this block to a Kafka topic"""
    LOG_FILTER = auto()
    """LOG_FILTER producer will respect log_filter topics while producing transaction hashes to a Kafka topic"""
