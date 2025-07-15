# app/db/automap.py
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.asyncio import AsyncEngine

AutomapBase = automap_base()

def snake_to_camel(s: str) -> str:
    """floor_plans → FloorPlan"""
    parts = s.rstrip("s").split("_")
    return "".join(word.capitalize() for word in parts)

async def init_automap(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(
            AutomapBase.prepare,
            reflect=True,
            classname_for_table=lambda base, tbl_name, tbl_obj: snake_to_camel(tbl_name),
        )
