#!/usr/bin/env python3
"""Stub MCP server - read-only over API"""
import os, sys, json
BASE = os.getenv("CLINICOPS_API_URL","http://localhost:8000")
TOKEN = os.getenv("FS_TOKEN","")
print(f"MCP server ready at {BASE} (token {'set' if TOKEN else 'missing'})", file=sys.stderr)
