import asyncio
import httpx

from worker_manager import get_idle_workers, mark_busy, mark_idle


async def send_job(worker, meeting_code, passcode, bot_count, duration_minutes):
    """
    Send job to a single worker.
    """

    url = worker["url"].rstrip("/") + "/api/start-bots"

    payload = {
        "meeting_code": meeting_code,
        "passcode": passcode,
        "bot_count": bot_count,
        "duration_minutes": duration_minutes
    }

    try:
        mark_busy(worker["worker_id"])

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)

        mark_idle(worker["worker_id"])

        return {
            "worker": worker["worker_id"],
            "status": response.status_code,
            "response": response.json()
        }

    except Exception as e:

        mark_idle(worker["worker_id"])

        return {
            "worker": worker["worker_id"],
            "status": "failed",
            "error": str(e)
        }


async def dispatch(meeting_code, passcode, bot_count, duration_minutes):

    workers = get_idle_workers()

    if len(workers) == 0:
        return {
            "success": False,
            "message": "No online workers available."
        }

    remaining = bot_count

    tasks = []

    for worker in workers:

        if remaining <= 0:
            break

        bots = min(5, remaining)

        tasks.append(
            send_job(
                worker,
                meeting_code,
                passcode,
                bots,
                duration_minutes
            )
        )

        remaining -= bots

    results = await asyncio.gather(*tasks)

    return {
        "success": True,
        "requested_bots": bot_count,
        "started_bots": bot_count - remaining,
        "remaining_bots": remaining,
        "workers_used": len(tasks),
        "results": results
    }
