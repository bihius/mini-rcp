#!/usr/bin/env python3
"""
SMB Connectivity Test Script
Tests network connectivity to SMB server and share access.
"""
import socket
import platform
import os
import sys

def test_network_connectivity(server, port=445):
    """Test basic network connectivity to SMB port"""
    print(f"Testing network connectivity to {server}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server, port))
        sock.close()

        if result == 0:
            print(f"✅ Network connectivity to {server}:{port} is OK")
            return True
        else:
            print(f"❌ Cannot connect to {server}:{port}. Error code: {result}")
            return False
    except Exception as e:
        print(f"❌ Network connectivity test failed: {e}")
        return False

def test_unc_path_access(unc_path):
    """Test direct UNC path access"""
    print(f"Testing UNC path access to {unc_path}...")
    try:
        if os.path.exists(unc_path):
            print(f"✅ UNC path {unc_path} is accessible")
            # Try to list directory
            if os.path.isdir(unc_path):
                files = os.listdir(unc_path)
                print(f"   Directory contains {len(files)} items")
            else:
                print("   Path is a file")
            return True
        else:
            print(f"❌ UNC path {unc_path} does not exist or is not accessible")
            return False
    except Exception as e:
        print(f"❌ UNC path access failed: {e}")
        return False

def test_smb_connection(server, share):
    """Test SMB connection using pysmb"""
    print(f"Testing SMB connection to {server}/{share}...")
    try:
        from smb.SMBConnection import SMBConnection
        import socket

        # Try anonymous connection
        conn = SMBConnection('', '', socket.gethostname(), server, use_ntlm_v2=True)
        if conn.connect(server, 445):
            print("✅ Anonymous SMB connection successful")

            # Try to list share contents
            try:
                shares = conn.listShares()
                share_names = [s.name for s in shares]
                if share in share_names:
                    print(f"✅ Share '{share}' exists")
                    # Try to list directory
                    try:
                        files = conn.listPath(share, '/')
                        print(f"   Share contains {len(files)} items in root")
                    except Exception as list_e:
                        print(f"   Could not list share contents: {list_e}")
                else:
                    print(f"❌ Share '{share}' not found. Available shares: {share_names}")
            except Exception as share_e:
                print(f"❌ Could not list shares: {share_e}")

            conn.close()
            return True
        else:
            print("❌ SMB connection failed")
            return False
    except Exception as e:
        print(f"❌ SMB connection test failed: {e}")
        return False

def main():
    print("SMB Connectivity Diagnostic Tool")
    print("=" * 40)

    # Configuration
    server = "pl-nas"
    share = "common"
    test_file = "it/m3group/RCP/PREvents.csv"

    print(f"Server: {server}")
    print(f"Share: {share}")
    print(f"Test file: {test_file}")
    print()

    # Test 1: Network connectivity
    network_ok = test_network_connectivity(server, 445)
    print()

    if not network_ok:
        print("❌ Basic network connectivity failed. Possible issues:")
        print("   - SMB server is down")
        print("   - Firewall blocking SMB traffic (port 445)")
        print("   - DNS resolution issues")
        print("   - Network connectivity problems")
        print()
        return

    # Test 2: UNC path access
    unc_base = f"\\\\{server}\\{share}"
    unc_ok = test_unc_path_access(unc_base)
    print()

    # Test 3: SMB connection
    smb_ok = test_smb_connection(server, share)
    print()

    # Summary
    print("Summary:")
    print(f"Network: {'✅' if network_ok else '❌'}")
    print(f"UNC Access: {'✅' if unc_ok else '❌'}")
    print(f"SMB Connection: {'✅' if smb_ok else '❌'}")

    if unc_ok:
        print("\n✅ UNC path access works! The application should be able to use direct file access.")
    elif smb_ok:
        print("\n✅ SMB connection works! The application should be able to connect.")
    else:
        print("\n❌ All connection methods failed. Possible solutions:")
        print("   1. Check if the SMB server is running")
        print("   2. Verify network connectivity")
        print("   3. Check firewall settings")
        print("   4. Verify share permissions")
        print("   5. Try accessing the share manually in Windows Explorer")

if __name__ == "__main__":
    main()