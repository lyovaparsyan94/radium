import sys
from pathlib import Path

import httpx

# Добавляем директорию src в sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import hashlib
from pathlib import Path

import aiofiles
import pytest
from aioresponses import aioresponses

from async_filehandler import URL, download_file, calculate_sha256, main


@pytest.mark.asyncio
async def test_download_file(tmp_path: Path) -> None:
    """Test the download_file function."""
    filename = tmp_path / "test_file.zip"
    with aioresponses() as m:
        m.get(URL, body=b"fake content", headers={'content-length': '12'})
        await download_file(URL, filename)

    assert filename.exists()
    async with aiofiles.open(filename, 'rb') as f:
        content = await f.read()
    assert content == b"fake content"


def test_calculate_sha256(tmp_path: Path) -> None:
    """Test the calculate_sha256 function."""
    filename = tmp_path / "test_file.zip"
    content = b"fake content"
    with open(filename, 'wb') as f:
        f.write(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    calculated_hash = calculate_sha256(filename)

    assert calculated_hash == expected_hash


@pytest.mark.asyncio
async def test_main(monkeypatch, tmp_path: Path) -> None:
    """Test the main function."""
    filenames = [tmp_path / f'project_configuration_{i}.zip' for i in range(3)]
    monkeypatch.setattr(Path, "resolve", lambda _: tmp_path)

    with aioresponses() as m:
        m.get(URL, body=b"fake content", headers={'content-length': '12'})
        await main()

    for filename in filenames:
        assert filename.exists()
        async with aiofiles.open(filename, 'rb') as f:
            content = await f.read()
        assert content == b"fake content"

    # Проверка на совпадение хэшей всех файлов
    expected_hash = hashlib.sha256(b"fake content").hexdigest()
    for filename in filenames:
        calculated_hash = calculate_sha256(filename)
        assert calculated_hash == expected_hash


@pytest.mark.asyncio
async def test_download_file_error_handling(tmp_path: Path) -> None:
    """Test error handling in the download_file function."""
    filename = tmp_path / "test_file.zip"
    with aioresponses() as m:
        m.get(URL, status=404)  # Имитируем ошибку 404
        with pytest.raises(httpx.HTTPStatusError):
            await download_file(URL, filename)

    assert not filename.exists()

@pytest.mark.asyncio
async def test_main_with_error(monkeypatch, tmp_path: Path) -> None:
    """Test the main function with one of the downloads failing."""
    filenames = [tmp_path / f'project_configuration_{i}.zip' for i in range(3)]
    monkeypatch.setattr(Path, "resolve", lambda _: tmp_path)

    with aioresponses() as m:
        m.get(URL, body=b"fake content", headers={'content-length': '12'}, repeat=2)
        m.get(URL, status=500)  # Имитируем ошибку на третьем запросе

        with pytest.raises(httpx.HTTPStatusError):
            await main()

    for i, filename in enumerate(filenames):
        if i < 2:
            assert filename.exists()
            async with aiofiles.open(filename, 'rb') as f:
                content = await f.read()
            assert content == b"fake content"
        else:
            assert not filename.exists()
