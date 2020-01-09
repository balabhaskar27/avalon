# Copyright 2020 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from utility.hex_utils import is_valid_hex_str
import binascii
from os import environ

from avalon_connector_sdk.interfaces.worker_registry_list_connector \
    import WorkerRegistryListConnector
from avalon_client_sdk.ethereum.ethereum_wrapper import EthereumWrapper
from avalon_client_sdk.utility.utils import construct_message
from avalon_client_sdk.utility.tcf_types import RegistryStatus

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


class EthereumWorkerRegistryListConnectorImpl(WorkerRegistryListConnector):
    """
    This class is to add/update registry entries of
    worker to Ethereum blockchain.
    """

    def __init__(self, config):
        if self.__validate(config):
            self.__initialize(config)
        else:
            raise Exception("Invalid or missing config parameter")

    def registry_add(self, org_id, uri, sc_addr, app_type_ids):
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return construct_message("failed", "Invalid Org id")
            if (sc_addr is not None and is_valid_hex_str(
                    binascii.hexlify(sc_addr).decode("utf8")) is False):
                logging.info("Invalid smart contract address {}")
                return construct_message(
                    "failed", "Invalid smart contract address")
            if (not uri):
                logging.info("Empty uri {}".format(uri))
                return construct_message("failed", "Empty uri")
            for aid in app_type_ids:
                if (is_valid_hex_str(binascii.hexlify(aid).decode("utf8"))
                        is False):
                    logging.info("Invalid application id {}".format(aid))
                    return construct_message(
                        "failed", "Invalid application id")

            txn_hash = self.__contract_instance.functions.registryAdd(
                org_id, uri, org_id, app_type_ids).buildTransaction(
                    self.__eth_client.get_transaction_params()
            )
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return construct_message(
                "failed",
                "direct registry contract instance is not initialized")

    def registry_update(self, org_id, uri, sc_addr, app_type_ids):
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.error("Invalid Org id {}".format(org_id))
                return construct_message("failed", "Invalid Org id")
            if (sc_addr is not None and is_valid_hex_str(
                    binascii.hexlify(sc_addr).decode("utf8")) is False):
                logging.error(
                    "Invalid smart contract address {}".format(sc_addr))
                return construct_message(
                    "failed", "Invalid smart contract address")
            if (not uri):
                logging.error("Empty uri {}".format(uri))
                return construct_message("failed", "Empty uri")
            for aid in app_type_ids:
                if (is_valid_hex_str(binascii.hexlify(aid).decode("utf8"))
                        is False):
                    logging.error("Invalid application id {}".format(aid))
                    return construct_message(
                        "failed", "Invalid application id")

            txn_hash = self.__contract_instance.functions.registryUpdate(
                org_id, uri, sc_addr,
                app_type_ids).buildTransaction(
                    self.__eth_client.get_transaction_params()
            )
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return construct_message(
                "failed",
                "direct registry contract instance is not initialized")

    def registry_set_status(self, org_id, status):
        if (self.__contract_instance is not None):
            if (is_valid_hex_str(binascii.hexlify(org_id).decode("utf8"))
                    is False):
                logging.info("Invalid Org id {}".format(org_id))
                return construct_message("failed", "Invalid argument")
            if not isinstance(status, RegistryStatus):
                logging.info("Invalid registry status {}".format(status))
                return construct_message(
                    "failed", "Invalid worker status {}".format(status))
            txn_hash = self.__contract_instance.functions.registrySetStatus(
                org_id,
                status.value).buildTransaction(
                    self.__eth_client.get_transaction_params()
            )
            tx = self.__eth_client.execute_transaction(txn_hash)
            return tx
        else:
            logging.error(
                "direct registry contract instance is not initialized")
            return construct_message(
                "failed",
                "direct registry contract instance is not initialized")

    def __validate(self, config):
        """
        validates parameter from config parameters for existence.
        Returns false if validation fails and true if it success
        """
        if config["ethereum"]["direct_registry_contract_file"] is None:
            logging.error("Missing direct registry contract file path!!")
            return False
        if config["ethereum"]["direct_registry_contract_address"] is None:
            logging.error("Missing direct registry contract address!!")
            return False
        return True

    def __initialize(self, config):
        """
        Initialize the parameters from config to instance variables.
        """
        self.__eth_client = EthereumWrapper(config)
        tcf_home = environ.get("TCF_HOME", "../../../")
        contract_file_name = tcf_home + "/" + \
            config["ethereum"]["direct_registry_contract_file"]
        contract_address = \
            config["ethereum"]["direct_registry_contract_address"]
        self.__contract_instance = self.__eth_client.get_contract_instance(
            contract_file_name, contract_address
        )
