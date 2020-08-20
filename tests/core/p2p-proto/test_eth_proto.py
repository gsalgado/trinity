import secrets

import pytest

from trinity._utils.assertions import assert_type_equality
from trinity._utils.timer import Timer
from trinity.protocol.eth.commands import (
    BlockBodiesV65,
    BlockHeadersV65,
    GetBlockBodiesV65,
    GetBlockHeadersV65,
    GetNodeDataV65,
    GetReceiptsV65,
    NewBlock,
    NewBlockHashes,
    NodeDataV65,
    ReceiptsV65,
    Status,
    Transactions,
    StatusV63,
)

from trinity.tools.factories import (
    BaseTransactionFieldsFactory,
    BlockBodyFactory,
    BlockHashFactory,
    BlockHeaderFactory,
    ReceiptFactory,
)
from trinity.tools.factories.common import (
    BlockHeadersQueryFactory,
)
from trinity.tools.factories.eth import (
    NewBlockHashFactory,
    NewBlockPayloadFactory,
    StatusPayloadFactory,
    StatusV63PayloadFactory,
)


@pytest.mark.parametrize(
    'command_type,payload',
    (
        (StatusV63, StatusV63PayloadFactory()),
        (Status, StatusPayloadFactory()),
        (NewBlockHashes, tuple(NewBlockHashFactory.create_batch(2))),
        (Transactions, tuple(BaseTransactionFieldsFactory.create_batch(2))),
        (GetBlockHeadersV65, BlockHeadersQueryFactory()),
        (GetBlockHeadersV65, BlockHeadersQueryFactory(block_number_or_hash=BlockHashFactory())),
        (BlockHeadersV65, tuple(BlockHeaderFactory.create_batch(2))),
        (GetBlockBodiesV65, tuple(BlockHashFactory.create_batch(2))),
        (BlockBodiesV65, tuple(BlockBodyFactory.create_batch(2))),
        (NewBlock, NewBlockPayloadFactory()),
        (GetNodeDataV65, tuple(BlockHashFactory.create_batch(2))),
        (NodeDataV65, (secrets.token_bytes(10), secrets.token_bytes(100))),
        (GetReceiptsV65, tuple(BlockHashFactory.create_batch(2))),
        (
            ReceiptsV65,
            (tuple(ReceiptFactory.create_batch(2)), tuple(ReceiptFactory.create_batch(3)))
        ),
    ),
)
@pytest.mark.parametrize(
    'snappy_support',
    (True, False),
)
def test_les_protocol_command_round_trips(command_type, payload, snappy_support):
    cmd = command_type(payload)
    message = cmd.encode(command_type.protocol_command_id, snappy_support=snappy_support)
    assert message.command_id == command_type.protocol_command_id
    result = command_type.decode(message, snappy_support=snappy_support)
    assert isinstance(result, command_type)
    assert result.payload == payload
    assert_type_equality(result.payload, payload)


def test_decode_perf():
    for cmd_type, factory in [(Transactions, BaseTransactionFieldsFactory),
                              (BlockBodiesV65, BlockBodyFactory)]:
        for snappy_support in (True, False):
            print("\n======= " + cmd_type.__name__ + "(snappy=" + str(snappy_support) + ") =======")
            for nitems in (1, 10, 100, 500, 1000):
                _measure_decode_perf(nitems, cmd_type, factory, snappy_support)


def _measure_decode_perf(nitems, cmd_type, factory, snappy_support):
    cmd = cmd_type(tuple(factory.create_batch(nitems)))
    message = cmd.encode(cmd_type.protocol_command_id, snappy_support)
    timer = Timer()
    for _ in range(10):
        cmd_type.decode(message, snappy_support=snappy_support)
    print("%d items (msg len: %d): %.5f" % (
        nitems,
        len(message.body) + len(message.header),
        timer.elapsed / 10)
    )
