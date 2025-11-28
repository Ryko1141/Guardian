# MT5 REST API Documentation

Complete documentation for the MT5 REST API implementation.

## 📚 Documentation Index

### Getting Started
- **[Quick Start Guide](MT5_API_QUICKSTART.md)** - Get up and running in 5 minutes
- **[Getting Started](MT5_API_GETTING_STARTED.md)** - Comprehensive beginner guide
- **[Quick Reference](MT5_API_QUICK_REFERENCE.md)** - Quick lookup for commands and endpoints

### Complete Reference
- **[REST API Reference](MT5_REST_API.md)** - Full API documentation with all endpoints
- **[Implementation Details](MT5_API_IMPLEMENTATION.md)** - Technical implementation overview
- **[Architecture](MT5_API_ARCHITECTURE.md)** - System architecture and design
- **[File Index](MT5_API_FILE_INDEX.md)** - Complete list of all related files
- **[Summary](MT5_API_SUMMARY.md)** - Implementation summary and statistics

## 🚀 Quick Links

### For New Users
1. Start with [Quick Start Guide](MT5_API_QUICKSTART.md)
2. Read [Getting Started](MT5_API_GETTING_STARTED.md) for detailed instructions
3. Use [Quick Reference](MT5_API_QUICK_REFERENCE.md) for common tasks

### For Developers
1. Review [REST API Reference](MT5_REST_API.md) for complete endpoint documentation
2. Check [Implementation Details](MT5_API_IMPLEMENTATION.md) for technical information
3. See [Architecture](MT5_API_ARCHITECTURE.md) for system design

### For Integration
1. See examples in `examples/api/`
2. Interactive docs: http://localhost:8000/docs
3. Test server: `python run_mt5_api.py`

## 📖 What's Inside

### MT5_API_QUICKSTART.md
- 5-minute setup guide
- Installation steps
- Common use cases
- Troubleshooting

### MT5_API_GETTING_STARTED.md
- Prerequisites
- Detailed setup
- Multiple client examples (Python, cURL, JavaScript)
- Security notes

### MT5_REST_API.md
- Complete API reference
- All 15+ endpoints documented
- Request/response examples
- Security best practices
- Production deployment guide

### MT5_API_QUICK_REFERENCE.md
- Quick command reference
- Endpoint table
- Code snippets
- Troubleshooting table

### MT5_API_IMPLEMENTATION.md
- Technical overview
- Files created
- Security features
- Testing results
- Performance considerations

### MT5_API_ARCHITECTURE.md
- System architecture diagrams
- Component interaction
- Data flow
- Session management

### MT5_API_FILE_INDEX.md
- Complete file listing
- File descriptions
- Statistics
- Quick access guide

### MT5_API_SUMMARY.md
- Implementation summary
- Feature checklist
- Statistics
- Validation results

## 🎯 Common Tasks

### Start the Server
```bash
python run_mt5_api.py
```

### Test the API
```bash
python tests/test_mt5_api.py
```

### Use Python Client
```python
from examples.api.test_mt5_api import MT5ApiClient

client = MT5ApiClient()
client.login(account, password, server)
# ... use API
client.logout()
```

### Open Web Client
Open `examples/api/mt5_api_client.html` in browser

## 📞 Support

- **Interactive Docs**: http://localhost:8000/docs
- **Examples**: See `examples/api/` folder
- **Issues**: Check troubleshooting sections in documentation

## 📝 Notes

All documentation is in Markdown format and can be viewed in:
- GitHub
- VS Code
- Any markdown reader
- Plain text editor

---

**Last Updated**: November 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅
