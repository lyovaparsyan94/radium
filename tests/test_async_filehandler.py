import inspect
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock
import hashlib
import pytest
import aiofiles
import aiohttp
from aioresponses import aioresponses
import subprocess

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from async_filehandler import URL, download_file, calculate_sha256, main, run_main

TEMP_DIR = Path(__file__).resolve().parent / "tmp_test_files"
TEMP_DIR.mkdir(exist_ok=True)


@pytest.mark.asyncio
async def download_test_file(url: str, filename: Path) -> None:
    """Download a test file to be used for comparison."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            async with aiofiles.open(filename, 'wb') as file:
                async for chunk in response.content.iter_chunked(8192):
                    await file.write(chunk)


def test_calculate_sha256() -> None:
    """Test the calculate_sha256 function."""
    filename = TEMP_DIR / "test_file.zip"
    content = b"fake content"
    with open(filename, 'wb') as f:
        f.write(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    calculated_hash = calculate_sha256(filename)

    assert calculated_hash == expected_hash
    filename.unlink()


@pytest.mark.asyncio
async def test_main(monkeypatch) -> None:
    """Test the main function."""
    filename = TEMP_DIR / 'project_configuration.zip'
    monkeypatch.setattr(Path, "resolve", lambda _: TEMP_DIR)

    if not filename.exists():
        await download_test_file(URL, filename)

    with aioresponses() as m:
        m.head(URL, headers={'Content-Length': '36'})
        m.get(URL, body=b"fake content" * 3, headers={'Content-Range': 'bytes 0-11/36'}, repeat=3)

        await main()

    test_file_path = TEMP_DIR / 'project_configuration.zip'
    expected_hash = calculate_sha256(test_file_path)
    calculated_hash = calculate_sha256(filename)
    assert calculated_hash == expected_hash
    filename.unlink()


def test_run_main():
    """Test the run_main function which calls asyncio.run(main())."""
    with patch("async_filehandler.main", new_callable=AsyncMock) as mock_main:
        with patch("asyncio.run") as mock_run:
            run_main()
            mock_run.assert_called_once()
            mock_main.assert_called_once()
            assert inspect.iscoroutine(mock_run.call_args[0][0])


def test_run_main_subprocess():
    """Test the script execution as a subprocess."""
    script_path = Path(__file__).resolve().parent.parent / "src" / "async_filehandler.py"
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0
