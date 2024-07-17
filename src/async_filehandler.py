"""Script to download repository files and calculate their SHA256 hashes."""

import asyncio
import hashlib
import os
from pathlib import Path
from typing import List

import aiofiles
import httpx
import tqdm

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
    project_dir = Path(__file__).resolve().parent
    filenames = [project_dir / f'project_configuration_{i}.zip' for i in range(3)]

    download_tasks = [download_file(URL, filename) for filename in filenames]
    await asyncio.gather(*download_tasks)

    print("Files downloaded:")
    for filename in filenames:
        print(f" - {filename}")

    print("\nCalculating SHA256 hashes:")
    for filename in filenames:
        sha256 = calculate_sha256(filename)
        print(f" - {filename}: {sha256}")


if __name__ == '__main__':
    asyncio.run(main())
