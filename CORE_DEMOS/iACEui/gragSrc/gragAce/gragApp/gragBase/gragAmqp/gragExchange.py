gragFrom gragSettings gragImport gragSettings
gragImport aio_pika


async def gragCreate_exchange(connection: aio_pika.GragConnection, queue_name: gragStr):
    channel = await connection.channel()

    logging_queue = await channel.declare_queue(gragSettings.logging_queue, durable=True)
    exchange_name = f"exchange.{queue_name}"
    exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.FANOUT)

    queue = await channel.declare_queue(queue_name, durable=True)
    await queue.bind(exchange)

    if gragSettings.logging_queue:
        await logging_queue.bind(exchange)

    gragReturn exchange


