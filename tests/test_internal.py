import asyncio
import json

from galaxy.api.plugin import Plugin
from galaxy.api.consts import Platform

def test_get_capabilites(reader, writer, read, write):
    class PluginImpl(Plugin): #pylint: disable=abstract-method
        async def get_owned_games(self):
            pass

    request = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "get_capabilities"
    }
    token = "token"
    plugin = PluginImpl(Platform.Generic, "0.1", reader, writer, token)
    read.side_effect = [json.dumps(request).encode() + b"\n", b""]
    asyncio.run(plugin.run())
    response = json.loads(write.call_args[0][0])
    assert response == {
        "jsonrpc": "2.0",
        "id": "3",
        "result": {
            "platform_name": "generic",
            "features": [
                "ImportOwnedGames"
            ],
            "token": token
        }
    }

def test_shutdown(plugin, read, write):
    request = {
        "jsonrpc": "2.0",
        "id": "5",
        "method": "shutdown"
    }
    read.side_effect = [json.dumps(request).encode() + b"\n", b""]
    asyncio.run(plugin.run())
    plugin.shutdown.assert_called_with()
    response = json.loads(write.call_args[0][0])
    assert response == {
        "jsonrpc": "2.0",
        "id": "5",
        "result": None
    }

def test_ping(plugin, read, write):
    request = {
        "jsonrpc": "2.0",
        "id": "7",
        "method": "ping"
    }
    read.side_effect = [json.dumps(request).encode() + b"\n", b""]
    asyncio.run(plugin.run())
    response = json.loads(write.call_args[0][0])
    assert response == {
        "jsonrpc": "2.0",
        "id": "7",
        "result": None
    }

def test_tick_before_handshake(plugin, read):
    read.side_effect = [b""]
    asyncio.run(plugin.run())
    plugin.tick.assert_not_called()

def test_tick_after_handshake(plugin, read):
    request = {
        "jsonrpc": "2.0",
        "id": "6",
        "method": "initialize_cache",
        "params": {"data": {}}
    }
    read.side_effect = [json.dumps(request).encode() + b"\n", b""]
    asyncio.run(plugin.run())
    plugin.tick.assert_called_with()
