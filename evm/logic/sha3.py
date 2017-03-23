import logging

try:
    from sha3 import keccak_256
except ImportError:
    from sha3 import sha3_256 as keccak_256

from evm import constants
from evm.exceptions import (
    OutOfGas,
)

from evm.utils.numeric import (
    ceil32,
    big_endian_to_int,
    int_to_big_endian,
)


logger = logging.getLogger('evm.logic.sha3')


def sha3(computation):
    start_position = big_endian_to_int(computation.stack.pop())
    size = big_endian_to_int(computation.stack.pop())

    computation.extend_memory(start_position, size)

    sha3_bytes = computation.memory.read(start_position, size)
    word_count = ceil32(len(sha3_bytes)) // 32

    gas_cost = constants.GAS_SHA3WORD * word_count
    computation.gas_meter.consume_gas(gas_cost, reason="SHA3: word gas cost")

    if computation.gas_meter.is_out_of_gas:
        raise OutOfGas("Out of gas computing SHA3")

    result = keccak_256(sha3_bytes).digest()

    logger.info("SHA3: %s -> %s", sha3_bytes, result)

    computation.stack.push(result)
