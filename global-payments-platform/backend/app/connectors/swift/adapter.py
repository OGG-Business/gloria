import httpx
import paramiko
import os
from typing import Optional

class SwiftConnector:
    def __init__(self, settings):
        self.settings = settings
        self.mode = settings.connector_swift_mode
        self.protocol = settings.connector_swift_protocol.upper()
        self.endpoint = settings.connector_swift_endpoint
        self.cert = (settings.connector_swift_tls_client_cert_path, settings.connector_swift_tls_client_key_path)
        self.verify = settings.connector_swift_tls_ca_chain_path

    async def ping(self) -> str:
        if self.protocol in ("REST", "AS4"):
            async with httpx.AsyncClient(verify=self.verify, cert=self.cert, timeout=20) as client:
                r = await client.get(self.endpoint + "/ping")
                r.raise_for_status()
                return r.text
        elif self.protocol == "SFTP":
            return self._sftp_ping()
        else:
            raise RuntimeError("Unsupported protocol")

    async def submit_pacs008(self, xml: str) -> str:
        if self.mode != "live":
            raise RuntimeError("Connector is not in live mode; not submitting")
        if self.protocol == "REST":
            return await self._submit_rest(xml)
        if self.protocol == "AS4":
            return await self._submit_as4(xml)
        if self.protocol == "SFTP":
            return self._submit_sftp(xml)
        raise RuntimeError("Unsupported protocol")

    async def _submit_rest(self, xml: str) -> str:
        headers = {"Content-Type": "application/xml"}
        async with httpx.AsyncClient(verify=self.verify, cert=self.cert, timeout=60) as client:
            r = await client.post(self.endpoint + "/payments/pacs008", content=xml.encode(), headers=headers)
            r.raise_for_status()
            return r.text

    async def _submit_as4(self, xml: str) -> str:
        # For AS4 over HTTPS, envelope may be required by partner; submit to agreed endpoint
        headers = {"Content-Type": "application/soap+xml"}
        async with httpx.AsyncClient(verify=self.verify, cert=self.cert, timeout=60) as client:
            r = await client.post(self.endpoint + "/as4", content=xml.encode(), headers=headers)
            r.raise_for_status()
            return r.text

    def _sftp_client(self) -> paramiko.SSHClient:
        host = self.settings.connector_swift_sftp_host
        if not host:
            raise RuntimeError("SFTP host not configured")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        key_path = self.settings.connector_swift_sftp_key_path
        if key_path and os.path.exists(key_path):
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
            ssh.connect(host, port=self.settings.connector_swift_sftp_port, username=self.settings.connector_swift_sftp_username, pkey=pkey)
        else:
            ssh.connect(host, port=self.settings.connector_swift_sftp_port, username=self.settings.connector_swift_sftp_username, password=self.settings.connector_swift_sftp_password)
        return ssh

    def _sftp_ping(self) -> str:
        ssh = self._sftp_client()
        try:
            sftp = ssh.open_sftp()
            sftp.listdir(self.settings.connector_swift_sftp_remote_dir or '.')
            sftp.close()
            return "OK"
        finally:
            ssh.close()

    def _submit_sftp(self, xml: str) -> str:
        remote_dir = self.settings.connector_swift_sftp_remote_dir or "/inbound"
        ssh = self._sftp_client()
        try:
            sftp = ssh.open_sftp()
            remote_path = os.path.join(remote_dir, "pacs008.xml")
            with sftp.file(remote_path, 'w') as f:
                f.write(xml)
            sftp.close()
            return "Uploaded"
        finally:
            ssh.close()