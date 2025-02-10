import threading
from contextlib import contextmanager

import attr


@attr.s(slots=True)
class Settings:
    """

    :param strict: boolean to indicate if the lxml should be parsed a 'strict'.
      If false then the recover mode is enabled which tries to parse invalid
      XML as best as it can.
    :type strict: boolean
    :param raw_response: boolean to skip the parsing of the XML response by
     zeep but instead returning the raw data

    :param forbid_dtd: disallow XML with a <!DOCTYPE> processing instruction
    :type forbid_dtd: bool
    :param forbid_entities: disallow XML with <!ENTITY> declarations inside the DTD
    :type forbid_entities: bool
    :param forbid_external: disallow any access to remote or local resources
      in external entities or DTD and raising an ExternalReferenceForbidden
      exception when a DTD or entity references an external resource.
    :type forbid_external: bool
    :param xml_huge_tree: disable lxml/libxml2 security restrictions and
                          support very deep trees and very long text content

    :param force_https: Force all connections to HTTPS if the WSDL is also
      loaded from an HTTPS endpoint. (default: true)
    :type force_https: bool
    :param extra_http_headers: Additional HTTP headers to be sent to the
     transport. This can be used in combination with the context manager
     approach to add http headers for specific calls.
    :type extra_headers: list

    :param xsd_ignore_sequence_order: boolean to indicate whether to enforce sequence
     order when parsing complex types. This is a workaround for servers that
     don't respect sequence order.
    :type xsd_ignore_sequence_order: boolean
    """

    strict = attr.ib(default=True)
    raw_response = attr.ib(default=False)

    # transport
    force_https = attr.ib(default=True)
    extra_http_headers = attr.ib(default=None)

    # lxml processing
    xml_huge_tree = attr.ib(default=False)
    forbid_dtd = attr.ib(default=False)
    forbid_entities = attr.ib(default=True)
    forbid_external = attr.ib(default=True)

    # xsd workarounds
    xsd_ignore_sequence_order = attr.ib(default=False)

    soap_env_prefix = attr.ib(default="soap-env")

    _tls = attr.ib(default=attr.Factory(threading.local))

    @contextmanager
    def __call__(self, **options):
        current = {}
        for key, value in options.items():
            current[key] = getattr(self, key)
            setattr(self._tls, key, value)

        try:
            yield
        finally:
            for key, value in current.items():
                default = getattr(self, key)
                if value == default:
                    delattr(self._tls, key)
                else:
                    setattr(self._tls, key, value)

    def __getattribute__(self, key):
        if key != "_tls" and hasattr(self._tls, key):
            return getattr(self._tls, key)
        return super().__getattribute__(key)

    def __init__(
        self,
        strict=True,
        raw_response=False,
        forbid_dtd=True,
        forbid_entities=True,
        forbid_external=True,
        xml_huge_tree=False,
        force_https=True,
        extra_http_headers=None,
        soap_env_prefix="soap-env"
    ):
        self.strict = strict
        self.raw_response = raw_response
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities
        self.forbid_external = forbid_external
        self.xml_huge_tree = xml_huge_tree
        self.force_https = force_https
        self.extra_http_headers = extra_http_headers or {}
        self.soap_env_prefix = soap_env_prefix
