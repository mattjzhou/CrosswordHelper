import asyncio
import logging
import logging.handlers
from asyncio import TimeoutError

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError


def initLogger(module="default", level=logging.INFO):
    log = logging.getLogger(module)
    log.handlers = []
    log.setLevel(level=level)
    # fileHandler = logging.handlers.RotatingFileHandler(
    #     f"{module}.log", maxBytes=0.5 * 10**9, backupCount=3
    # )
    fileFormatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
    )
    # fileHandler.setFormatter(fileFormatter)
    # log.addHandler(fileHandler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fileFormatter)
    log.addHandler(console_handler)
    return log


async def getUrl(
    log: logging.Logger,
    session: ClientSession,
    url,
    params=None,
    headers=None,
    retries=5,
    retryDelay=15,
    json=False,
):
    log.info(f"Requesting from {url}")
    try:
        async with session.get(
            url,
            params=params,
            headers=headers,
        ) as resp:
            if resp.status == 200:
                if json:
                    return await resp.json()
                return await resp.content.read()
            else:
                log.error(f"Received {resp}")
    except ClientConnectorError as e:
        log.error(f"Received ClientConnectorError: {e}")
    except TimeoutError as e:
        log.error(f"Received TimeoutError: {e}")
    except Exception as e:
        log.error(f"Received Exception: {e}", exc_info=True)
    for retry in range(1, retries + 1):
        await asyncio.sleep(
            retryDelay * (2**retry)
        )  # exponential backoff (.5, 1, 2, 4, 8) min
        log.warning(f"Retry {retry} of {retries} from {url}")
        try:
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status == 200:
                    if json:
                        return await resp.json()
                    return await resp.content.read()
                else:
                    log.error(f"Received {resp}")
        except ClientConnectorError as e:
            log.error(f"Received ClientConnectorError: {e}")
        except TimeoutError as e:
            log.error(f"Received TimeoutError: {e}")
        except Exception as e:
            log.error(f"Received Exception: {e}", exc_info=True)
    log.critical(f"Unable to get URL after {retries} retries")
