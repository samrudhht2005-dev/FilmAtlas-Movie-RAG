import os
import urllib.parse
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import (
    AuthError,
    CertificateConfigurationError,
    ConfigurationError,
    DriverError,
    Neo4jError,
    ServiceUnavailable,
)

load_dotenv(override=True)


def get_config_value(key, default=None):
    """Retrieve configuration from Streamlit secrets if running in Streamlit, otherwise environment."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


def get_neo4j_config():
    """Extract and sanitize Neo4j connection parameters without exposing secrets."""
    raw_uri = get_config_value("NEO4J_URI", "")
    username = get_config_value("NEO4J_USERNAME", "neo4j")
    password = get_config_value("NEO4J_PASSWORD", "")
    database = get_config_value("NEO4J_DATABASE")

    uri = (raw_uri or "").strip().strip("'\"")
    username = (username or "neo4j").strip().strip("'\"")
    password = (password or "").strip().strip("'\"")
    database = (database or "").strip().strip("'\"") or None

    # If user provided a hostname without scheme, default to neo4j+s:// for Aura
    if uri and "://" not in uri:
        uri = f"neo4j+s://{uri}"

    return uri, username, password, database


def extract_hostname(uri):
    """Safely extract hostname from connection URI."""
    try:
        parsed = urllib.parse.urlparse(uri if "://" in uri else f"neo4j://{uri}")
        return parsed.hostname or uri
    except Exception:
        return uri


def diagnose_connection_error(error, uri="", username=""):
    """Produce clear, actionable diagnostic messages without revealing secrets."""
    error_str = str(error)
    error_type = type(error).__name__
    hostname = extract_hostname(uri)

    # 1. DNS resolution failure (Windows Errno 11001, getaddrinfo failed, etc.)
    if "11001" in error_str or "getaddrinfo failed" in error_str.lower() or "dns" in error_str.lower():
        return (
            f"DNS Resolution Error: Unable to resolve hostname '{hostname}'.\n"
            f"Diagnostics:\n"
            f"  • The domain '{hostname}' does not exist in DNS or cannot be reached.\n"
            f"  • For Neo4j Aura: Free instances automatically pause after inactivity or may be deleted. "
            f"Check your instance status or resume it at https://console.neo4j.io/.\n"
            f"  • If you have a newly created or resumed instance, update NEO4J_URI in .env with the new Bolt URI.\n"
            f"  • Check if a VPN, proxy, or firewall is blocking DNS resolution for *.databases.neo4j.io."
        )

    # 2. Authentication failure
    if isinstance(error, AuthError) or "unauthorized" in error_str.lower() or "authentication failure" in error_str.lower():
        hint = ""
        if username != "neo4j":
            hint = f" (Note: NEO4J_USERNAME is currently '{username}', but the default Aura admin user is 'neo4j'.)"
        return (
            f"Authentication Failed: Invalid credentials for user '{username}'.{hint}\n"
            f"Please verify NEO4J_USERNAME and NEO4J_PASSWORD in your .env file."
        )

    # 3. SSL / TLS Security errors
    if isinstance(error, CertificateConfigurationError) or "ssl" in error_str.lower() or "certificate" in error_str.lower():
        return (
            f"Security/TLS Error: Failed to establish a secure SSL/TLS connection to '{hostname}'.\n"
            f"Ensure your URI uses 'neo4j+s://' (or 'bolt+s://') for Aura instances."
        )

    # 4. Service unavailable / Connection refused
    if isinstance(error, ServiceUnavailable) or "connection refused" in error_str.lower():
        return (
            f"Service Unavailable: Could not establish a connection to '{hostname}' on port 7687.\n"
            f"Please ensure the Neo4j instance is currently running and accepting traffic."
        )

    return f"{error_type}: {error_str}"


def get_driver():
    """Create and return a Neo4j driver using sanitized configuration."""
    uri, username, password, _ = get_neo4j_config()

    if not uri or not password:
        raise ValueError(
            "Please configure NEO4J_URI and NEO4J_PASSWORD in your .env file."
        )

    return GraphDatabase.driver(
        uri,
        auth=(username, password),
    )


def verify_connection():
    """Verify connectivity to Neo4j with structured error reporting."""
    driver = None
    uri, username, _, _ = get_neo4j_config()
    try:
        driver = get_driver()
        driver.verify_connectivity()
        return True, "Connected to Neo4j successfully!"
    except ValueError as val_err:
        return False, str(val_err)
    except Exception as error:
        return False, diagnose_connection_error(error, uri, username)
    finally:
        if driver is not None:
            driver.close()


def run_query(query, parameters=None):
    """Execute a Cypher query safely and return records."""
    driver = None
    uri, username, _, database = get_neo4j_config()
    try:
        driver = get_driver()
        session_kwargs = {}
        if database:
            session_kwargs["database"] = database
        with driver.session(**session_kwargs) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    except Exception as error:
        raise RuntimeError(diagnose_connection_error(error, uri, username)) from error
    finally:
        if driver is not None:
            driver.close()

