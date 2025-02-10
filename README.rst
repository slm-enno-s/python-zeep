========================
Zeep: Python SOAP client
========================

A Python SOAP client

Highlights:
 * Compatible with Python 3.7, 3.8, 3.9, 3.10, 3.11 and PyPy3
 * Build on top of lxml, requests and httpx
 * Support for Soap 1.1, Soap 1.2 and HTTP bindings
 * Support for WS-Addressing headers
 * Support for WSSE (UserNameToken / x.509 signing)
 * Support for asyncio using the httpx module
 * Experimental support for XOP messages


Please see for more information the documentation at
http://docs.python-zeep.org/


.. start-no-pypi

Status
------


**I consider this library to be stable. Since no new developments happen around the SOAP specification it won't be updated that much. Good PR's which fix bugs are always welcome however.**


.. image:: https://readthedocs.org/projects/python-zeep/badge/?version=latest
    :target: https://readthedocs.org/projects/python-zeep/

.. image:: https://github.com/mvantellingen/python-zeep/workflows/Python%20Tests/badge.svg
    :target: https://github.com/mvantellingen/python-zeep/actions?query=workflow%3A%22Python+Tests%22

.. image:: http://codecov.io/github/mvantellingen/python-zeep/coverage.svg?branch=master
    :target: http://codecov.io/github/mvantellingen/python-zeep?branch=master

.. image:: https://img.shields.io/pypi/v/zeep.svg
    :target: https://pypi.python.org/pypi/zeep/

.. end-no-pypi

Installation
------------

.. code-block:: bash

    pip install zeep

Note that the latest version to support Python 2.7, 3.3, 3.4 and 3.5 is Zeep
3.4, install via `pip install zeep==3.4.0`

Zeep uses the lxml library for parsing xml. See
https://lxml.de/installation.html for the installation requirements.

Usage
-----
.. code-block:: python

    from zeep import Client

    client = Client('tests/wsdl_files/example.rst')
    client.service.ping()


To quickly inspect a WSDL file use::

    python -m zeep <url-to-wsdl>

To connect with the KvK SOAP Dataservice (https://www.kvk.nl/producten-bestellen/handelsregister-dataservice/aansluitendataservice/overheid/aansluiten/) you can use the following code. This will connect with the preproduction server with test data only. You will need a valid public/private key pair that is registered also on the KvK side. Furthermore, you need to combine their public certificates into one .cer file so it can be used to verify the responses you get back from their server.

Different products are on different WSDL's with different WS-A addressed, so update accordingly. A list of product can be found on the given URL, together with their public certificates and a lot of other technical info.

.. code-block:: python

    from zeep import Client, Settings
    from requests import Session
    from zeep.transports import Transport
    from zeep.cache import SqliteCache
    from zeep.wsse import BinarySignatureTimestamp
    from zeep.wsa import WsAddressingPlugin
    from zeep.wsa import RemoveWSA
    
    
    session = Session()
    session.cert = ('client.pem', 'privkey.pem')
    transport = Transport(session=session, cache=SqliteCache())
    
    settings = Settings(strict=False, xml_huge_tree=True)
    
    client = Client('http://schemas.kvk.nl/contracts/kvk/dataservice/catalogus/2015/02/KVK-KvKDataservice.wsdl', 
                      settings=settings,
                      transport=transport,
                      plugins=[
                        RemoveWSA(), 
                        WsAddressingPlugin(address_url = 'http://es.kvk.nl/kvk-DataservicePP/2015/02', remove_urn_from_id = True)
                      ],
                      wsse=BinarySignatureTimestamp(
                        "privkey.pem", 
                        "client.pem",
                        "_password_",
                        sign_wsa_elements = ["To", "MessageID", "Action"],
                        response_certfile = 'webservices.preprod.kvk.nl.cabundle.cer'))
    
    service = client.create_service("{http://schemas.kvk.nl/schemas/hrip/dataservice/2015/02}DataserviceSoap11", "https://webservices.preprod.kvk.nl/postbus1")
    
    result = service.ophalenInschrijving(**{"klantreferentie": "", "kvkNummer": "90003128"})


WSSE Signature with Inclusive Namespaces
--------------------------------------
When signing SOAP messages with WS-Security signatures, you can specify which namespace prefixes should be treated as inclusive during canonicalization. This is useful when working with services that require specific namespace handling:

.. code-block:: python

    from zeep.wsse import Signature
    
    # Configure signature with inclusive namespaces per element
    signature = Signature(
        key_file='privkey.pem',
        certfile='cert.pem',
        inclusive_namespaces={
            'Body': ['soap', 'ns1'],       # Specific prefixes for Body element
            'Timestamp': ['wsu', 'wsse'],  # Specific prefixes for Timestamp
            'default': ['soap']            # Default prefixes for other elements
        }
    )

    client = Client(
        'http://example.com/service?wsdl',
        wsse=signature
    )

The inclusive_namespaces parameter accepts a dictionary where:
 * Keys are element names ('Body', 'Timestamp', etc) or 'default'
 * Values are lists of namespace prefixes to treat as inclusive
 * The 'default' key specifies prefixes for elements without specific configuration
 * If no inclusive namespaces are needed, omit the parameter or pass an empty dict


Support
=======

Please see the documentation at http://docs.python-zeep.org for more
information.

If you want to report a bug then please first read
http://docs.python-zeep.org/en/master/reporting_bugs.html

Please only report bugs and not support requests to the GitHub issue tracker.
