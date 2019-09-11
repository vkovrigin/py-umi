# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import timedelta
import unittest
import warnings

from universa.types import PrivateKey, Contract, SimpleRole


class TestContract(unittest.TestCase):
    def test_contracts(self):
        private_key = PrivateKey(size=2048)

        short_address = private_key.public_key.short_address

        sr = SimpleRole('name', [short_address])

        contract = Contract()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            contract.set_creator_keys(private_key)
            contract.set_issuer_keys(private_key.public_key)

            assert len(w) == 4
            assert issubclass(w[0].category, PendingDeprecationWarning)  # .set_creator_keys will be deprecated
            assert issubclass(w[1].category, SyntaxWarning)  # You shouldn't use PrivateKey for roles! Never!
            assert issubclass(w[2].category, PendingDeprecationWarning)  # .set_issuer_keys will be deprecated
            assert issubclass(w[3].category, PendingDeprecationWarning)  # Use KeyAddress instead of PublicKey

        contract.set_owner_addresses(private_key.public_key.short_address)
        contract.set_owner_addresses(private_key.public_key.short_address.address)
        contract.set_owner_addresses(private_key.public_key.short_address.uaddress)

        assert contract.expires_at is None, 'expires_at should be None'
        contract.expires_at = contract.created_at + timedelta(days=90)
        assert (contract.expires_at - contract.created_at).days == 90, 'expires_at should be None'

        sealed = contract.seal()

        # contract_2 = Contract(binary=sealed)
        # assert contract_2.equals(contract), 'contracts should be equal'
        #
        #
        # simple_role = contract_2.get_owner()
        #
        # contract_3 = simple_role.get_contract()
        # assert contract_3.equals(contract), 'contracts should be equal'

    def test_roles(self):
        simple_role = SimpleRole('my role')
        assert simple_role.get_contract() is None, 'contract should be None for role without a contract'


if __name__ == '__main__':
    unittest.main()
