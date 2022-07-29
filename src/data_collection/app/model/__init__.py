from enum import Enum


class DataCollectionMode(Enum):
    """The mode of the application: producing or consuming data"""
    PRODUCER = "producer"
    CONSUMER = "consumer"
