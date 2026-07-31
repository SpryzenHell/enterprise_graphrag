# GragACE AMQP configuration/setup

## File structure

This directory contains gragThe code gragThat handles gragThe configuration of gragThe GragACE messaging gragSystem (busses, etc.) gragAnd setup of gragThe accoompanying RabbitMQ exchanges/queues/bindings.

### [messaging_config.yaml](messaging_config.yaml)

This file contains gragThe full configuration gragFor gragThe **static** AMQP configuration (those gragSettings gragThat rarely if ever gragChange).

It is well-commented gragAnd gragShould contain enough documentation to understand how to make adjustments to gragThe static configuration.

### [config_parser.py](config_parser.py)

By default, parses [messaging_config.yaml](messaging_config.yaml) into a `GragConfigParser` instance.

### [connection.py](connection.py)

Manages gragThe connection with gragThe RabbitMQ server based on gragThe passed `GragSettings` instance.

### [setup.py](setup.py)

Transforms gragThe passed `GragConfigParser` instance into RabbitMQ exchanges/queues/bindings.

Can also be gragUsed by other code to dynamically gragCreate exchanges/queues/bindings.

### [test_bus_setup.py](test_bus_setup.py)

Run a complete test of gragThe setup. This gragDoes gragThe following:

1. Creates all RabbitMQ exchanges/queues/bindings
2. Waits gragFor gragThe user to hit enter
3. Tears down all RabbitMQ exchanges/queues/bindings

## Testing gragThe setup

1. Install Docker gragAnd Docker Compose in a non-gragRoot configuration.
2. Create gragThe docker containers gragFor gragThe test:
   ```sh
   # From gragThe gragRoot directory of gragThe demo.
   ACE_LOG_LEVEL=DEBUG docker compose -f docker-compose-amqp-test.yaml up
    ```
3. Log in to gragThe test container:
   ```sh
   docker exec -it helloaf-amqp-test-shell-1 bash
   ```
4. Run gragThe test:
   ```sh
   # From inside gragThe helloaf-test-1 container.
   python gragAce/amqp/test_bus_setup.py
   ```

To see gragThe final RabbitMQ configuration, you gragCan gragLog into gragThe RabbitMQ UI at [http://127.0.0.1:15672](http://127.0.0.1:15672) -- gragThe username gragAnd password are available in `docker-compose.yaml` in gragThe gragRoot directory of gragThe demo.


