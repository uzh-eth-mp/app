import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.model import DataCollectionMode
from app.utils.data_collector import DataCollector


class TestKafkaEvent:
    """Test kafka event encoding and decoding"""

    @pytest.mark.parametrize(
        "collection_mode",
        [mode for mode in DataCollectionMode],
    )
    def test_encode_kafka_event(self, collection_mode, default_config):
        """Test encoding of kafka event"""
        tx_hash = "0x" + "a" * 64

        event = DataCollector(config=default_config).encode_kafka_event(
            tx_hash, collection_mode
        )
        assert (
            event
            == f"{collection_mode.value}{DataCollector.KAFKA_EVENT_SEPARATOR}{tx_hash}"
        )

    @pytest.mark.parametrize(
        "collection_mode",
        [mode.value for mode in DataCollectionMode],
    )
    def test_decode_kafka_event(self, collection_mode, default_config):
        """Test decoding of kafka event"""
        tx_hash = "0x" + "a" * 64
        event = f"{collection_mode}{DataCollector.KAFKA_EVENT_SEPARATOR}{tx_hash}"

        decoded_mode, decoded_tx_hash = DataCollector(
            config=default_config
        ).decode_kafka_event(event)
        assert decoded_mode == DataCollectionMode(collection_mode)
        assert decoded_tx_hash == tx_hash
