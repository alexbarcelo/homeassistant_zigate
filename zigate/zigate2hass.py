#! /usr/bin/python3
import logging
from asyncio import Protocol

from homeassistant.helpers.dispatcher import (dispatcher_send)
from homeassistant.components import persistent_notification

from .const import *
from pyzigate.zgt_parameters import *
from pyzigate.interface import ZiGate

_LOGGER = logging.getLogger(__name__)


class ZiGateProtocol(Protocol):

    def connection_made(self, transport):
        _LOGGER.debug('ZIGATE : Transport initialized : %s' % transport)
        self.transport = transport

    def data_received(self, data):
        try:
            self.device.read_data(data)
        except:
            _LOGGER.debug('ZIGATE : Data received but not ready {!r}'.
                          format(data.decode()))

    def connection_lost(self, exc):
        _LOGGER.debug('ZIGATE : Connection Lost !')


class ZiGate2HASS(ZiGate):

    def __init__(self, hass):
        super().__init__()
        self.hass = hass

    def set_device_property(self, addr, endpoint, property_id, property_data):
        # decoding the address to assign the proper signal (bytes --> str)
        if endpoint:
            addrep = ZGT_SIGNAL_UPDATE.format(addr.decode() + endpoint.decode())
        else:
            addrep = ZGT_SIGNAL_UPDATE.format(addr.decode())

        _LOGGER.debug('ZIGATE SIGNAL :')
        _LOGGER.debug('- Signal   : {}'.format(addrep))
        _LOGGER.debug('- Property : {}'.format(property_id))
        _LOGGER.debug('- Data     : {}'.format(property_data))
        dispatcher_send(self.hass, addrep, property_id, property_data)

    def set_external_command(self, cmd, **msg):
        if cmd == ZGT_CMD_NEW_DEVICE:
            addr = msg['addr']
            persistent_notification.async_create(self.hass, 'New device {} paired !'.
                                                 format(addr), 
                                                 title='Zigate Breaking News !')
            # requesting endpoint list
            #print('endpoint list for {}'.format(addr))
            #self.hass.services.async_call(DOMAIN, 'raw_command',
            #                     {'cmd':'0045', 'data':addr})
        elif cmd == ZGT_CMD_LIST_ENDPOINTS:
            ep_list = '\n'.join(msg['endpoints'])
            title = 'Endpoint list for device {} :'.format(msg['addr'])
            persistent_notification.async_create(self.hass, ep_list, title=title)


