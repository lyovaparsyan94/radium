import asyncio
import hashlib
import logging
import tempfile
from pathlib import Path
import aiofiles
import aiohttp

URL = "https://gitea.radium.group/radium/project-configuration/archive/master.zip"
CHUNK_SIZE = 8192

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def download_chunk(url: str, filename: Path, start: int, end: int, chunk_id: int) -> None:
    headers = {'Range': f'bytes={start}-{end}'}
    logger.info(f"Starting download chunk {chunk_id}: {start}-{end}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            async with aiofiles.open(filename, 'wb') as file:
                async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                    await file.write(chunk)
    logger.info(f"Completed download chunk {chunk_id}: {start}-{end}")


async def download_file(url: str, filename: Path) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as response:
            response.raise_for_status()
            total_size = int(response.headers['Content-Length'])
            part_size = total_size // 3

            tasks = [
                download_chunk(url, filename.with_suffix(f'.part{i}'), i * part_size, (i + 1) * part_size - 1, i)
                for i in range(3)
            ]

            await asyncio.gather(*tasks)

    # Combine parts
    async with aiofiles.open(filename, 'wb') as file:
        for i in range(3):
            part_filename = filename.with_suffix(f'.part{i}')
            async with aiofiles.open(part_filename, 'rb') as part_file:
                while True:
                    chunk = await part_file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    await file.write(chunk)
            part_filename.unlink()
    logger.info(f"Completed file download and merge: {filename}")


def calculate_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with file_path.open('rb') as file:
        for byte_block in iter(lambda: file.read(CHUNK_SIZE), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        filename = temp_path / 'project_configuration.zip'

        await download_file(URL, filename)

        sha256 = calculate_sha256(filename)
        logger.info(f"SHA256: {sha256}")


def run_main():
    asyncio.run(main())


if __name__ == '__main__':
    run_main()
