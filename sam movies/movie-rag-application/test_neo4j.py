
import sys
import socket
from services.neo4j_connection import (
    get_neo4j_config,
    extract_hostname,
    verify_connection,
    get_driver,
    diagnose_connection_error,
)


def test_neo4j():
    print("=" * 60)
    print("       NEO4J CONNECTIVITY & DIAGNOSTIC TEST")
    print("=" * 60)

    uri, username, password, database = get_neo4j_config()

    if not uri or not password:
        print("[CONFIG ERROR]: NEO4J_URI and NEO4J_PASSWORD must be set in .env")
        return False

    hostname = extract_hostname(uri)
    masked_user = username if username else "(empty)"
    db_info = database or "default (neo4j)"

    print(f"[*] Target URI:     {uri}")
    print(f"[*] Hostname:       {hostname}")
    print(f"[*] Username:       {masked_user}")
    print(f"[*] Database:       {db_info}")
    print(f"[*] Password:       [CONFIGURED - {len(password)} chars]")
    print("-" * 60)

    # Step 1: DNS Resolution Check
    print(f"[*] Step 1: Resolving DNS for '{hostname}' on port 7687...")
    try:
        addr_info = socket.getaddrinfo(hostname, 7687, socket.AF_UNSPEC, socket.SOCK_STREAM)
        ip_addresses = sorted(list({entry[4][0] for entry in addr_info}))
        print(f"[+] DNS Resolution SUCCESS: Resolved to {ip_addresses}")
    except socket.gaierror as dns_err:
        print(f"[-] DNS Resolution FAILED: {dns_err}")
        print("\nDiagnostic Details:")
        print(diagnose_connection_error(dns_err, uri, username))
        print("=" * 60)
        return False

    # Step 2: Driver Connectivity Check
    print(f"\n[*] Step 2: Testing Neo4j driver connectivity...")
    success, message = verify_connection()
    if success:
        print(f"[+] {message}")
        print("=" * 60)
        print("SUCCESS: Connection to Neo4j database is fully operational!")
        print("=" * 60)
        return True
    else:
        print(f"[-] Connection FAILED:\n{message}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    ok = test_neo4j()
    sys.exit(0 if ok else 1)

