# pylint: disable=W0613:unused-argument,E0601,E0602:undefined-variable,C0114,C0115,C0116
from typing import Dict, Optional, List, Set

class Permissions:
    @staticmethod
    def default_for_user(user_id: str): ...
    def add_retrieve_permissions(self, retrieve: List[str]): ...
    def add_update_permissions(self, update: List[str]): ...
    def add_delete_permissions(self, delete: List[str]): ...
    def add_compute_permissions(self, compute: Dict[str, List[str]]): ...
    def is_retrieve_allowed(self, user_id: str) -> bool: ...
    def is_update_allowed(self, user_id: str) -> bool: ...
    def is_delete_allowed(self, user_id: str) -> bool: ...
    def is_compute_allowed(self, user_id: str, program: str) -> bool: ...
    def is_retrieve_permissions_allowed(self, user_id: str) -> bool: ...
    def is_update_permissions_allowed(self, user_id: str) -> bool: ...

class NodeKey:
    """
     This is a :py:class:`NodeKey` class that
    contains a private key used by the
    underlying libp2p to form multiaddress and
    identity secrets. This class is consumed by :py:class:`NillionClient`
    class to initialize a client.

    This object's constructors can be used via the following
    class methods:

    1. From string encoded in Base58 (:py:meth:`from_base58`);
    2. From a file (:py:meth:`from_file`);
    3. From a seed (:py:meth:`from_seed`).

    Example
    -------

    .. code-block:: py3

        from py_nillion_client import NodeKey
        node_key = NodeKey.from_seed('my_seed')
    """

    @classmethod
    def from_file(cls, path: str): ...
    @classmethod
    def from_base64(cls, contents: str): ...
    @classmethod
    def from_seed(cls, seed: str): ...

class ConnectionMode:
    """Specifies a socket address structure for a listening client connection.

    This mode is suited for clients that are backend services.

    Arguments
    ---------
    str
      Socket address structure.

    Returns
    -------
    ConnectionMode

    Example
    -------

    .. code-block:: py3

      connection_mode = ConnectionMode.direct('0.0.0.0:11337')
    """

    @classmethod
    def direct(cls, listen_address: str): ...
    @classmethod
    def relay(cls): ...
    @classmethod
    def dialer(cls): ...

class UserKey:
    """This is a :py:class:`UserKey` class that
    contains the public and private keys for the user.
    This class is used by :py:class:`NillionClient`
    class to initialize a client.

    This object's constructors can be used via the following
    class methods:

    1. From string encoded in Base58 (:py:meth:`from_base58`);
    2. From a file (:py:meth:`from_file`);
    3. From scratch (:py:meth:`generate`);
    4. From seed (:py:meth:`seed`).
    """

    @classmethod
    def generate(cls): ...
    @classmethod
    def from_file(cls, path: str): ...
    @classmethod
    def from_base64(cls, contents: str): ...
    @classmethod
    def from_seed(cls, seed: str): ...

class ClusterDescriptor:
    def id(self) -> str: ...
    def parties(self) -> List[str]: ...
    def prime(self) -> str: ...
    def polynomial_degree(self) -> int: ...
    def kappa(self) -> int: ...

class ProgramBindings:
    def __init__(self, program_id: str): ...
    def add_input_party(self, name: str, party_id: str): ...
    def add_output_party(self, name: str, party_id: str): ...

class Integer:
    value: int

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: Integer) -> bool: ...

class UnsignedInteger:
    value: int

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: UnsignedInteger) -> bool: ...

class NadaValue:
    value: object

class NadaValues:
    def __init__(self, values: Dict[str, NadaValue]): ...
    def dict(self) -> Dict[str, NadaValue]: ...

class SecretInteger:
    value: int

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: SecretInteger) -> bool: ...

class SecretUnsignedInteger:
    value: int

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: SecretUnsignedInteger) -> bool: ...

class SecretNonZeroInteger:
    value: int

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: SecretInteger) -> bool: ...

class SecretNonZeroUnsignedInteger:
    value: int

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: SecretUnsignedInteger) -> bool: ...

class SecretArray:
    value: object

    def __init__(self, value: List[object]): ...
    def __len__(self) -> int: ...

class SecretBlob:
    value: bytearray

    def __init__(self, value: bytearray): ...

# Compute events
class FinalResult:
    value: object

class ComputeFinishedEvent:
    uuid: str
    result: FinalResult

class ComputeScheduledEvent:
    uuid: str

class PaymentReceipt:
    pass

# The Nillion client
class NillionClient:
    user_id: str
    party_id: str
    build_version: str

    def __init__(
        self,
        node_key: NodeKey,
        bootnodes: List[str],
        connection_mode: ConnectionMode,
        user_key: UserKey,
        whitelist: Optional[Set[str]] = None,
    ) -> None: ...
    async def store_values(
        self,
        cluster_id: str,
        values: NadaValues,
        permissions: Optional[Permissions],
        receipt: PaymentReceipt,
    ): ...
    async def delete_values(self, cluster_id: str, store_id: str): ...
    async def retrieve_value(self, cluster_id: str, store_id: str, secret_id: str): ...
    async def update_values(
        self,
        cluster_id: str,
        store_id: str,
        update_values: NadaValues,
        receipt: PaymentReceipt,
    ): ...
    async def store_program(
        self,
        cluster_id: str,
        program_name: str,
        program_mir_path: str,
        receipt: PaymentReceipt,
    ): ...
    async def compute(
        self,
        cluster_id: str,
        bindings: ProgramBindings,
        store_ids: List[str],
        values: NadaValues,
        receipt: PaymentReceipt,
    ) -> str: ...
    async def cluster_information(self, cluster_id: str) -> ClusterDescriptor: ...
    async def next_compute_event(self) -> object: ...
    async def retrieve_permissions(
        self, cluster_id: str, store_id: str, receipt: PaymentReceipt
    ) -> Permissions: ...
    async def update_permissions(
        self,
        cluster_id: str,
        store_id: str,
        permissions: Permissions,
        receipt: PaymentReceipt,
    ) -> str: ...

def version() -> str: ...
