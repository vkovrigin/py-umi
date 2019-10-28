# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .base import Base
from .hash_id import HashId


class Client(Base):
    JAVA_CLASS = 'com.icodici.universa.node2.network.Client'

    def __init__(self, topology_input, topology_cache_dir, client_private_key, **kwargs):
        self.topology_input = topology_input
        self.topology_cache_dir = topology_cache_dir
        self.client_private_key = client_private_key
        super(Client, self).__init__()

    def _instantiate_data(self):
        return (self.topology_input,
                self.topology_cache_dir,
                self.client_private_key.remote
                    if isinstance(self.client_private_key, Base)
                    else self.client_private_key)

    def get_version(self):
        return self._invoke('getVersion')

    def get_state(self, hash_id):
        """
        :type hash_id: HashId
        :rtype: dict
        """
        return self._invoke('getState', hash_id)

    def register_parcel_with_state(self, packed, millis_to_wait):
        """
        Register the contract on the network using parcel (to provide payment)
        that waits until registration is complete for a given amount of time.

        :param bytes packed: Parcel binary
        :param int millis_to_wait: maximum time to wait for final ItemState
        :rtype: dict
        """
        return self._invoke('registerParcelWithState', packed, millis_to_wait)
