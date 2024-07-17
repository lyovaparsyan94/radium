import asyncio
import hashlib
import tempfile
import logging
from pathlib import Path

import aiofiles
import httpx
import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

URL = "https://gitea.radium.group/radium/project-configuration/archive/master.zip"
CHUNK_SIZE = 8192


async def download_file(url: str, filename: Path) -> None:
    """Download a file from a URL and save it locally."""
    async with aiofiles.open(filename, 'wb') as file:
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', url) as response:
                response.raise_for_status()
                total = int(response.headers.get('content-length', 0))
                tqdm_params = {
                    'desc': str(filename),
                    'total': total,
                    'miniters': 1,
                    'unit': 'B',
                    'unit_scale': True,
                    'unit_divisor': 1024,
                }
                with tqdm.tqdm(**tqdm_params) as progress_bar:
                    async for chunk in response.aiter_bytes(CHUNK_SIZE):
                        progress_bar.update(len(chunk))
                        await file.write(chunk)


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with file_path.open('rb') as file:
        for byte_block in iter(lambda: file.read(CHUNK_SIZE), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def main() -> None:
    """Main function to download files and calculate their hashes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        filenames = [temp_path / f'project_configuration_{i}.zip' for i in range(3)]

        download_tasks = [download_file(URL, filename) for filename in filenames]
        await asyncio.gather(*download_tasks)

        logger.info("Files downloaded:")
        for filename in filenames:
            logger.info(f" - {filename}")

        logger.info("\nCalculating SHA256 hashes:")
        for filename in filenames:
            sha256 = calculate_sha256(filename)
            logger.info(f" - {filename}: {sha256}")

        logger.info("All files have been processed. Temporary files will be deleted.")


def run_main():
    """Run the main function using asyncio.run."""
    asyncio.run(main())


if __name__ == '__main__':
    run_main()
