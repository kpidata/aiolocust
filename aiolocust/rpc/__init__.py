import warnings

try:
    from aiolocust.rpc import zmqrpc as rpc
except ImportError:
    warnings.warn("WARNING: Using pure Python socket RPC implementation instead of zmq. "
                  "If running in distributed mode, this could cause a performance decrease. "
                  "We recommend you to install the pyzmq python package when running in distributed mode.")
    from aiolocust.rpc import socketrpc as rpc

from aiolocust.rpc.protocol import Message
