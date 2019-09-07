from eth_utils import decode_hex

from eth2.beacon.constants import GWEI_PER_ETH
from eth2.beacon.typing import Epoch, Gwei, Second, Slot
from eth2.configs import Eth2Config

from eth_utils import decode_hex

MINIMAL_SERENITY_CONFIG = Eth2Config(
    # Misc
    SHARD_COUNT=8,
    TARGET_COMMITTEE_SIZE=4,
    MAX_VALIDATORS_PER_COMMITTEE=4096,
    MIN_PER_EPOCH_CHURN_LIMIT=4,
    CHURN_LIMIT_QUOTIENT=65536,
    SHUFFLE_ROUND_COUNT=10,
    # Genesis
    MIN_GENESIS_ACTIVE_VALIDATOR_COUNT=64,
    MIN_GENESIS_TIME=1578009600,  # (= Jan 3, 2020)
    # Gwei values
    MIN_DEPOSIT_AMOUNT=Gwei(2 ** 0 * GWEI_PER_ETH),  # (= 1,000,000,000) Gwei
    MAX_EFFECTIVE_BALANCE=Gwei(2 ** 5 * GWEI_PER_ETH),  # (= 32,000,000,00) Gwei
    EJECTION_BALANCE=Gwei(2 ** 4 * GWEI_PER_ETH),  # (= 16,000,000,000) Gwei
    EFFECTIVE_BALANCE_INCREMENT=Gwei(2 ** 0 * GWEI_PER_ETH),  # (= 1,000,000,000) Gwei
    # Initial values
    GENESIS_SLOT=Slot(0),
    GENESIS_EPOCH=Epoch(0),
    BLS_WITHDRAWAL_PREFIX=0,
    # Time parameters
    SECONDS_PER_SLOT=Second(6),  # seconds
    MIN_ATTESTATION_INCLUSION_DELAY=2 ** 0,  # (= 1) slots
    SLOTS_PER_EPOCH=8,
    MIN_SEED_LOOKAHEAD=2 ** 0,  # (= 1) epochs
    ACTIVATION_EXIT_DELAY=2 ** 2,  # (= 4) epochs
    SLOTS_PER_ETH1_VOTING_PERIOD=16,
    SLOTS_PER_HISTORICAL_ROOT=64,
    MIN_VALIDATOR_WITHDRAWABILITY_DELAY=256,
    PERSISTENT_COMMITTEE_PERIOD=2 ** 11,  # (= 2,048) epochs
    MAX_EPOCHS_PER_CROSSLINK=4,
    MIN_EPOCHS_TO_INACTIVITY_PENALTY=4,
    # State list lengths
    EPOCHS_PER_HISTORICAL_VECTOR=64,
    EPOCHS_PER_SLASHINGS_VECTOR=64,
    HISTORICAL_ROOTS_LIMIT=2 ** 24,
    VALIDATOR_REGISTRY_LIMIT=2 ** 40,
    # Reward and penalty quotients
    BASE_REWARD_FACTOR=2 ** 6,  # (= 64)
    WHISTLEBLOWER_REWARD_QUOTIENT=2 ** 9,  # (= 512)
    PROPOSER_REWARD_QUOTIENT=2 ** 3,
    INACTIVITY_PENALTY_QUOTIENT=2 ** 25,  # (= 33,554,432)
    MIN_SLASHING_PENALTY_QUOTIENT=2 ** 5,
    # Max operations per block
    MAX_PROPOSER_SLASHINGS=2 ** 4,  # (= 16)
    MAX_ATTESTER_SLASHINGS=2 ** 0,  # (= 1)
    MAX_ATTESTATIONS=2 ** 7,  # (= 128)
    MAX_DEPOSITS=2 ** 4,  # (= 16)
    MAX_VOLUNTARY_EXITS=2 ** 4,  # (= 16)
    MAX_TRANSFERS=0,
    # Deposit contract
    DEPOSIT_CONTRACT_ADDRESS=decode_hex(
        "0x1234567890123456789012345678901234567890"
    ),  # TBD
)
