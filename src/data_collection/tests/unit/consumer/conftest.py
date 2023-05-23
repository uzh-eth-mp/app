from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from app.consumer.tx_processor import TransactionProcessor


@pytest.fixture
def transaction_processor() -> TransactionProcessor:
    processor = TransactionProcessor(MagicMock(), Mock(), Mock())
    processor.db_manager.insert_transaction = AsyncMock()
    processor.db_manager.insert_transaction_logs = AsyncMock()
    processor.db_manager.insert_internal_transaction = AsyncMock()
    return processor
