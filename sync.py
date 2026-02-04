#!/usr/bin/env python3
"""
Sync Ricky's daily logs to EverMemOS.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from client import EverMemClient


async def sync_daily_log(client: EverMemClient, date: str, workspace: str):
    """Sync a single daily log."""
    log_path = os.path.join(workspace, f"memory/{date}.md")
    
    if not os.path.exists(log_path):
        print(f"  No log for {date}")
        return 0
    
    with open(log_path) as f:
        content = f.read()
    
    # Parse sections
    lines = content.split("\n")
    current_section = ""
    sections = []
    
    for line in lines:
        if line.startswith("## "):
            if current_section:
                sections.append(current_section)
            current_section = line + "\n"
        else:
            current_section += line + "\n"
    
    if current_section:
        sections.append(current_section)
    
    count = 0
    for section in sections:
        if len(section.strip()) > 50:  # Skip tiny sections
            mem_id = await client.store_memory(
                content=section[:2000],
                sender="ricky",
                metadata={"source": "daily_log", "date": date}
            )
            if mem_id:
                count += 1
                print(f"    ✓ {section.split(chr(10))[0][:50]}...")
    
    return count


async def sync_memory_md(client: EverMemClient, workspace: str):
    """Sync MEMORY.md (long-term memory)."""
    mem_path = os.path.join(workspace, "MEMORY.md")
    
    if not os.path.exists(mem_path):
        print("  No MEMORY.md found")
        return 0
    
    with open(mem_path) as f:
        content = f.read()
    
    # Split by ## headers
    sections = content.split("\n## ")
    count = 0
    
    for section in sections:
        if len(section.strip()) > 50:
            mem_id = await client.store_memory(
                content=f"## {section}"[:2000] if not section.startswith("#") else section[:2000],
                sender="ricky",
                metadata={"source": "MEMORY.md", "type": "long_term"}
            )
            if mem_id:
                count += 1
    
    return count


async def main():
    workspace = os.path.expanduser("~/.openclaw/workspace")
    client = EverMemClient()
    
    print("🔄 Ricky Memory Sync")
    print("=" * 50)
    
    # Check health
    if not await client.health_check():
        print("❌ EverMemOS not running")
        print("   Start with: docker compose up -d")
        await client.close()
        return
    
    print("✅ EverMemOS connected\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            # Sync MEMORY.md
            print("📚 Syncing MEMORY.md...")
            count = await sync_memory_md(client, workspace)
            print(f"   Synced {count} sections\n")
            
            # Sync recent daily logs
            print("📅 Syncing daily logs...")
            total = 0
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                print(f"  {date}:")
                count = await sync_daily_log(client, date, workspace)
                total += count
            print(f"\n   Total: {total} memories synced")
            
        else:
            # Sync specific date
            date = sys.argv[1]
            print(f"📅 Syncing {date}...")
            count = await sync_daily_log(client, date, workspace)
            print(f"   Synced {count} sections")
    else:
        # Sync today
        date = datetime.now().strftime("%Y-%m-%d")
        print(f"📅 Syncing {date}...")
        count = await sync_daily_log(client, date, workspace)
        print(f"   Synced {count} sections")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
