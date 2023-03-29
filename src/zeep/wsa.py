import uuid

from lxml import etree
from lxml.builder import ElementMaker

from zeep import ns
from zeep.plugins import Plugin
from zeep.wsdl.utils import get_or_create_header

WSA = ElementMaker(namespace=ns.WSA, nsmap={"wsa": ns.WSA})

class RemoveWSA(Plugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        env = envelope.find('{http://schemas.xmlsoap.org/soap/envelope/}Header')  
        for child in env:
            if child.tag.startswith('{http://www.w3.org/2005/08/addressing}'):
                env.remove(child)
        return envelope, http_headers



class WsAddressingPlugin(Plugin):
    nsmap = {"wsa": ns.WSA}

    def __init__(self, address_url: str = None, remove_urn_from_id = False):
        self.address_url = address_url
        self.remove_urn_from_id = remove_urn_from_id

    def egress(self, envelope, http_headers, operation, binding_options):
        """Apply the ws-addressing headers to the given envelope."""

        wsa_action = operation.abstract.wsa_action
        if not wsa_action:
            wsa_action = operation.soapaction

        header = get_or_create_header(envelope)
        headers = [
            WSA.Action(wsa_action),
            WSA.MessageID(("urn:" if not self.remove_urn_from_id else "") + "uuid:" + str(uuid.uuid4())),
            WSA.To(self.address_url or binding_options["address"]),
        ]
        header.extend(headers)

        # the top_nsmap kwarg was added in lxml 3.5.0
        if etree.LXML_VERSION[:2] >= (3, 5):
            etree.cleanup_namespaces(
                header, keep_ns_prefixes=header.nsmap, top_nsmap=self.nsmap
            )
        else:
            etree.cleanup_namespaces(header)
        return envelope, http_headers
