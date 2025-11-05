# mini-rcp

## Troubleshooting

### SMB Connectivity Issues

If you encounter `[WinError 10054] An existing connection was forcibly closed by the remote host` errors:

1. **Run the diagnostic script**:

   ```bash
   uv run python test-smb.py
   ```

2. **Check network connectivity**:

   - Ensure the SMB server is running and accessible
   - Verify firewall settings allow SMB traffic (port 445)
   - Test basic network connectivity: `ping pl-nas`

3. **Test manual access**:

   - Try accessing `\\pl-nas\common` in Windows Explorer
   - Verify you have permissions to access the share

4. **Temporary local testing**:
   - Copy `PREvents.csv` to the project root
   - Rename `config.json` to `config.json.backup`
   - Rename `config-local.json` to `config.json`
   - Run the application with local files

### Common Issues

- **DejaVu fonts not found**: PDF generation falls back to Helvetica automatically
- **SMB connection fails**: Application tries multiple authentication methods and UNC fallback
- **Archive path errors**: Ensure archive directories exist and are writable

### Logs

Check `logs/` directory for detailed error information:

- `logs/app.log` - Main application logs
- `logs/web.log` - Web server logs
- `logs/processor.log` - Background processor logs
