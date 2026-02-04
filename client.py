#!/usr/bin/env python3
"""
EverMemOS Client for Ricky

Connects Ricky's memory system to EverMemOS backend.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
import httpx


@dataclass
class Memory:
    """A stored memory."""
    id: str
    content: str
    sender: str
    timestamp: datetime
    metadata: dict


class EverMemClient:
    """Client for EverMemOS API."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.user_id = "ricky_twin"
    
    async def health_check(self) -> bool:
        """Check if EverMemOS is running."""
        try:
            resp = await self.client.get(f"{self.base_url}/health")
            return resp.status_code == 200
        except:
            return False
    
    async def store_memory(
        self,
        content: str,
        sender: str = "ricky",
        metadata: Optional[dict] = None
    ) -> Optional[str]:
        """Store a new memory."""
        try:
            resp = await self.client.post(
                f"{self.base_url}/api/v1/memories",
                json={
                    "message_id": f"msg_{datetime.now().timestamp()}",
                    "create_time": datetime.now().isoformat(),
                    "sender": sender,
                    "content": content,
                    "metadata": metadata or {}
                }
            )
            if resp.status_code == 200:
                return resp.json().get("id")
        except Exception as e:
            print(f"Store error: {e}")
        return None
    
    async def search_memories(
        self,
        query: str,
        limit: int = 10
    ) -> List[Memory]:
        """Search memories semantically."""
        try:
            resp = await self.client.get(
                f"{self.base_url}/api/v1/memories/search",
                params={
                    "query": query,
                    "user_id": self.user_id,
                    "retrieve_method": "hybrid",
                    "limit": limit
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                return [
                    Memory(
                        id=m.get("id", ""),
                        content=m.get("content", ""),
                        sender=m.get("sender", ""),
                        timestamp=datetime.fromisoformat(m.get("create_time", "")),
                        metadata=m.get("metadata", {})
                    )
                    for m in data.get("memories", [])
                ]
        except Exception as e:
            print(f"Search error: {e}")
        return []
    
    async def get_recent(self, limit: int = 20) -> List[Memory]:
        """Get recent memories."""
        try:
            resp = await self.client.get(
                f"{self.base_url}/api/v1/memories",
                params={"user_id": self.user_id, "limit": limit}
            )
            if resp.status_code == 200:
                data = resp.json()
                return [
                    Memory(
                        id=m.get("id", ""),
                        content=m.get("content", ""),
                        sender=m.get("sender", ""),
                        timestamp=datetime.fromisoformat(m.get("create_time", "")),
                        metadata=m.get("metadata", {})
                    )
                    for m in data.get("memories", [])
                ]
        except Exception as e:
            print(f"Recent error: {e}")
        return []
    
    async def close(self):
        await self.client.aclose()


class RickyMemoryBridge:
    """Bridge between Ricky's file-based memory and EverMemOS."""
    
    def __init__(self, workspace: str = "~/.openclaw/workspace"):
        import os
        self.workspace = os.path.expanduser(workspace)
        self.evermem = EverMemClient()
    
    async def sync_daily_log(self, date: str):
        """Sync a daily log file to EverMemOS."""
        import os
        
        log_path = os.path.join(self.workspace, f"memory/{date}.md")
        if not os.path.exists(log_path):
            print(f"No log for {date}")
            return
        
        with open(log_path) as f:
            content = f.read()
        
        # Split into sections
        sections = content.split("\n## ")
        
        for section in sections:
            if section.strip():
                # Store each section as a memory
                memory_id = await self.evermem.store_memory(
                    content=section[:2000],  # Limit size
                    sender="ricky",
                    metadata={"source": "daily_log", "date": date}
                )
                if memory_id:
                    print(f"  Stored: {section[:50]}...")
    
    async def query(self, question: str) -> str:
        """Query memories for relevant context."""
        memories = await self.evermem.search_memories(question, limit=5)
        
        if not memories:
            return "No relevant memories found."
        
        context = "\n\n".join([
            f"[{m.timestamp.strftime('%Y-%m-%d')}] {m.content[:500]}"
            for m in memories
        ])
        
        return context
    
    async def close(self):
        await self.evermem.close()


async def main():
    print("🧠 Ricky Memory Bridge")
    print("=" * 50)
    
    client = EverMemClient()
    
    # Check health
    if await client.health_check():
        print("✅ EverMemOS is running")
        
        # Store test memory
        mem_id = await client.store_memory(
            content="Testing EverMemOS integration from Ricky",
            sender="ricky"
        )
        print(f"Stored memory: {mem_id}")
        
        # Search
        results = await client.search_memories("test integration")
        print(f"Found {len(results)} memories")
    else:
        print("❌ EverMemOS not running")
        print("   Start with: docker compose up -d")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
