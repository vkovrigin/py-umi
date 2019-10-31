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

    def is_approved_by_network(self, item_id, trust_level, millis_to_wait):
        """
        Check if the contract has APPROVED status across the network. The method queries the status
        from multiple random different nodes until either gets enough replies to consider it approved,
        or collects a negative consensus sufficient to consider it is not approved (whatever happens earlier).
        “Enough” factor (for “enough replies”) is specified using the trustLevel parameter
        (what ratio of the total node count you would consider trusted).

        :param HashId item_id: to get state of
        :param float trust_level: a value from 0 (exclusive) to 0.9;
                                  how many nodes (of all ones available in the network) do you need
        :param int millis_to_wait: maximum time to get the positive or negative result from the network.
                                   If result is not received within given time ClientError is thrown
        :rtype: bool
        """
        return self._invoke('isApprovedByNetwork', item_id, trust_level, millis_to_wait)

    def register_parcel_with_state(self, packed, millis_to_wait):
        """
        Register the contract on the network using parcel (to provide payment)
        that waits until registration is complete for a given amount of time.

        :param bytes packed: Parcel binary
        :param int millis_to_wait: maximum time to wait for final ItemState
        :rtype: dict
        """
        return self._invoke('registerParcelWithState', packed, millis_to_wait)
