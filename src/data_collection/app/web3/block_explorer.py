from collections import namedtuple

from app.config import DataCollectionConfig
from app.db.manager import DatabaseManager


ExplorationBounds = namedtuple("ExplorationBounds", ["start_block", "end_block"])


class BlockExplorer:
    """Decide the start and end block numbers of the data collection process"""
    # Start from the genesis block by default
    DEFAULT_START_BLOCK = 0
    # End with the latest block by default
    DEFAULT_END_BLOCK = None

    def __init__(self, data_collection_cfg: DataCollectionConfig, db: DatabaseManager) -> None:
        self.cfg_start_block = data_collection_cfg.start_block
        self.cfg_end_block = data_collection_cfg.end_block
        self.db = db

    async def get_exploration_bounds(self) -> ExplorationBounds:
        """
        Determine the starting and ending block numbers based on configuration and database values

        Note:
            Configuration values take precedence over the database values.
        """
        # Default configuration
        start_block, end_block = self.DEFAULT_START_BLOCK, self.DEFAULT_END_BLOCK

        # Get latest inserted block from db
        last_block = None
        if res := await self.db.get_block():
            last_block = res["block_number"]

        # Get last processed block from db
        last_processed_block = None
        if res := await self.db.get_last_processed_block_number():
            last_processed_block = res["block_number"]

        # Get starting block from external sources if available
        if self.cfg_start_block is not None:
            # Give priority to config
            start_block = self.cfg_start_block
        elif last_block is not None:
            # If last block number contains a value, use this as the starting block number
            start_block = last_block
            if last_processed_block is not None and last_processed_block == last_block:
                # If the last processed block number is the same as last block number,
                # continue from the next block
                start_block += 1
            else:
                # Otherwise we have to start from the current last block because
                # something went wrong (last_processed_block is smaller than las block)
                pass

        # Get ending block if available in config
        if self.cfg_end_block is not None:
            end_block = self.cfg_end_block

        return ExplorationBounds(
            start_block=start_block,
            end_block=end_block
        )
