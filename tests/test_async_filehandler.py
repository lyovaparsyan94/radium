import inspect
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock
import hashlib
import pytest
from aioresponses import aioresponses
import subprocess

# Добавляем директорию src в sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from async_filehandler import URL, download_file, calculate_sha256, main, run_main

TEMP_DIR = Path(__file__).resolve().parent / "tmp_test_files"
TEMP_DIR.mkdir(exist_ok=True)


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
    filenames = [TEMP_DIR / f'project_configuration_{i}.zip' for i in range(3)]
    monkeypatch.setattr(Path, "resolve", lambda _: TEMP_DIR)

    with aioresponses() as m:
        m.get(URL, body=b"fake content", headers={'content-length': '12'})
        await main()

    expected_hash = hashlib.sha256(b"fake content").hexdigest()
    for filename in filenames:
        if filename.exists():
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
    assert "Files downloaded:" in result.stderr
    assert "Calculating SHA256 hashes:" in result.stderr
    assert "All files have been processed. Temporary files will be deleted." in result.stderr
