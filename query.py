#!/usr/bin/env python3
"""
Query Ricky's memories via EverMemOS.
"""

import asyncio
import sys
from client import EverMemClient


async def main():
    client = EverMemClient()
    
    print("🔍 Ricky Memory Query")
    print("=" * 50)
    
    # Check health
    if not await client.health_check():
        print("❌ EverMemOS not running")
        await client.close()
        return
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Query: ")
    
    print(f"\n🔎 Searching: {query}\n")
    
    memories = await client.search_memories(query, limit=5)
    
    if not memories:
        print("No memories found.")
    else:
        print(f"Found {len(memories)} relevant memories:\n")
        for i, m in enumerate(memories, 1):
            print(f"{'─'*50}")
            print(f"[{i}] {m.timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"    {m.content[:300]}...")
            print()
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
