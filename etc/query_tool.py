import asyncio
import argparse

import asyncpg


async def cmd_event(conn, args):
    """Event command handler

    Args:
        conn (asyncpg.Connection): connection to the database
        args (argparse.args): command line arguments
    """
    raise NotImplementedError()


async def cmd_supply(conn, args):
    """Supply command handler

    Args:
        conn (asyncpg.Connection): connection to the database
        args (argparse.args): command line arguments
    """
    # TODO: fix this method, needs to compute the total supply for a given address

    async with conn.transaction():
        # Postgres requires non-scrollable cursors to be created
        # and used in a transaction.

        # Create a Cursor object
        cur = await conn.cursor(
            "SELECT * FROM eth_contract_supply_change WHERE address = $1", args.address
        )

        # Move the cursor 10 rows forward
        await cur.forward(10)

        # Fetch one row and print it
        print(await cur.fetchrow())

        # Fetch a list of 5 rows and print it
        print(await cur.fetch(5))

    raise NotImplementedError()


async def main():
    parser = argparse.ArgumentParser(description="PostgreSQL query tool")
    # Set default function to None
    parser.set_defaults(func=None)
    parser.add_argument("--db-dsn", help="PostgreSQL DSN", required=True)

    # Create subparsers for commands
    subparsers = parser.add_subparsers(description="Available commands")

    # 'event' command
    parser_event = subparsers.add_parser(
        name="event", description="Selects transaction logs that contain an event"
    )
    parser_event.set_defaults(func=cmd_event)
    parser_event.add_argument(
        "-t", "--type", help="The event type (Transfer, Swap, ...)", required=True
    )
    parser_event.add_argument(
        "-a", "--address", help="Compute the total amount of events for a contract"
    )

    # 'supply' command
    parser_event = subparsers.add_parser(
        name="supply", description="Compute the total supply for a given contract"
    )
    parser_event.set_defaults(func=cmd_supply)
    parser_event.add_argument(
        "-a", "--address", help="Contract address to compute supply for", required=True
    )

    # Get the CLI arguments
    args = parser.parse_args()

    if args.func:
        dsn = args.db_dsn
        # Establish a postgres connection
        conn = await asyncpg.connect(dsn=dsn)

        try:
            # Execute the correct command
            await args.func(conn, args)
        finally:
            # Exit postgres
            await conn.close()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
