"""Synchronize PostgreSQL professional_tools and tool_categories tables
with verified bilingual data from tools_catalog_data.
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.tools import ProfessionalTool, ToolCategory
from app.templates.tools_catalog_data import ALL_VERIFIED_TOOLS, TOOL_CATEGORIES_DATA


async def sync_tools_catalog() -> None:
    print(f"Starting tools catalog sync: {len(TOOL_CATEGORIES_DATA)} categories, {len(ALL_VERIFIED_TOOLS)} tools...")
    async with AsyncSessionLocal() as session:
        # 1. Sync Categories
        category_cache: dict[str, uuid.UUID] = {}
        for cat_data in TOOL_CATEGORIES_DATA:
            res = await session.execute(
                select(ToolCategory).where(ToolCategory.slug == cat_data["slug"])
            )
            cat = res.scalar_one_or_none()
            if not cat:
                cat = ToolCategory(
                    id=uuid.uuid4(),
                    slug=cat_data["slug"],
                    name=cat_data["name_en"],
                    name_id=cat_data["name_id"],
                    description_en=cat_data["description_en"],
                    description_id=cat_data["description_id"],
                )
                session.add(cat)
                await session.flush()
                print(f"Created category: {cat_data['name_en']}")
            else:
                cat.name = cat_data["name_en"]
                cat.name_id = cat_data["name_id"]
                cat.description_en = cat_data["description_en"]
                cat.description_id = cat_data["description_id"]
            category_cache[cat_data["slug"]] = cat.id

        # 2. Sync Tools
        for t_data in ALL_VERIFIED_TOOLS:
            slug = t_data["slug"]
            cat_slug = t_data.get("category_slug", "clients")
            cat_id = category_cache.get(cat_slug)

            # Details dictionary contains all extended Section 5 research fields
            details = {
                "category_slug": cat_slug,
                "product_type": t_data.get("product_type", "Standalone Utility"),
                "summary_en": t_data.get("summary"),
                "summary_id": t_data.get("summary_id"),
                "repository_url": t_data.get("repository_url"),
                "download_url": t_data.get("download_url"),
                "overview_en": t_data.get("overview_en"),
                "overview_id": t_data.get("overview_id"),
                "primary_use_cases_en": t_data.get("primary_use_cases_en", []),
                "primary_use_cases_id": t_data.get("primary_use_cases_id", []),
                "explicit_boundaries_en": t_data.get("explicit_boundaries_en", []),
                "explicit_boundaries_id": t_data.get("explicit_boundaries_id", []),
                "features": t_data.get("features", []),
                "compatibility_matrix": t_data.get("compatibility_matrix", []),
                "security_considerations": t_data.get("security_considerations"),
                "getting_started": t_data.get("getting_started"),
                "practical_scenarios": t_data.get("practical_scenarios", []),
                "career_connections": t_data.get("career_connections", []),
                "knowledge_connections": t_data.get("knowledge_connections", []),
                "exercise_connections": t_data.get("exercise_connections", []),
                "alternatives": t_data.get("alternatives", []),
                "verified_sources": t_data.get("verified_sources", []),
                "content_reviewed_at": t_data.get("content_reviewed_at"),
            }

            res = await session.execute(
                select(ProfessionalTool).where(ProfessionalTool.slug == slug)
            )
            tool = res.scalar_one_or_none()
            if not tool:
                tool = ProfessionalTool(
                    id=uuid.uuid4(),
                    slug=slug,
                    name=t_data["name"],
                    vendor=t_data.get("vendor"),
                    category_id=cat_id,
                    category_slug=cat_slug,
                    publication_status=t_data.get("publication_status", "published"),
                    verification_status=t_data.get("verification_status", "verified"),
                    summary=t_data.get("summary"),
                    official_url=t_data.get("official_url"),
                    documentation_url=t_data.get("documentation_url"),
                    license_model=t_data.get("license_model"),
                    supported_platforms=t_data.get("supported_platforms", []),
                    supported_engines=t_data.get("supported_engines", []),
                    details=details,
                    last_verified_at=datetime.now(timezone.utc),
                )
                session.add(tool)
                print(f"Created tool: {t_data['name']}")
            else:
                tool.name = t_data["name"]
                tool.vendor = t_data.get("vendor")
                tool.category_id = cat_id
                tool.category_slug = cat_slug
                tool.publication_status = t_data.get("publication_status", "published")
                tool.verification_status = t_data.get("verification_status", "verified")
                tool.summary = t_data.get("summary")
                tool.official_url = t_data.get("official_url")
                tool.documentation_url = t_data.get("documentation_url")
                tool.license_model = t_data.get("license_model")
                tool.supported_platforms = t_data.get("supported_platforms", [])
                tool.supported_engines = t_data.get("supported_engines", [])
                tool.details = details
                tool.last_verified_at = datetime.now(timezone.utc)
                print(f"Updated tool: {t_data['name']}")

        await session.commit()
        print("Tools catalog successfully synchronized!")


if __name__ == "__main__":
    asyncio.run(sync_tools_catalog())
