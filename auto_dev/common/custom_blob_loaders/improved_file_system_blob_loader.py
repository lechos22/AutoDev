"""Use to load blobs from the local file system."""
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

from langchain.document_loaders import FileSystemBlobLoader


class ImprovedFileSystemBlobLoader(FileSystemBlobLoader):

    def __init__(self, path: Union[str, Path], *, glob: str = "**/[!.]*", exclude: Sequence[str] = (),
                 suffixes: Optional[Sequence[str]] = None, show_progress: bool = False) -> None:

        super().__init__(path, glob=glob, exclude=exclude, suffixes=suffixes, show_progress=show_progress)

    def _yield_paths(self) -> Iterable[Path]:
        """Yield paths that match the requested pattern."""
        paths = self.path.rglob(self.glob)
        excl_paths = set()

        if len(self.exclude) > 0:
            for excl_pattern in self.exclude:
                excl_paths = excl_paths.union({str(path) for path in self.path.rglob(excl_pattern)})

        for path in paths:
            if str(path) in excl_paths:
                continue
            if path.is_file():
                if self.suffixes and path.suffix not in self.suffixes:
                    continue
                yield path
