# photo-face-filter

Scans a folder of photos and copies the ones that contain at least one face into another folder. Originals are never moved or modified.

Uses the [`face_recognition`](https://github.com/ageitgey/face_recognition) library (dlib). Supports `.jpg`, `.jpeg` and `.png`.

## Installation

```
pip install face_recognition
```

On Windows, `face_recognition` depends on `dlib`, which needs a C++ compiler and CMake to build. If the install fails, use the prebuilt wheel instead:

```
pip install dlib-bin
pip install face_recognition --no-deps
pip install face_recognition_models Click numpy Pillow "setuptools<81"
```

`setuptools<81` is needed because `face_recognition_models` imports `pkg_resources`, which newer setuptools versions removed.

## Usage

```
python filter.py <source> [dest] [-r] [-m {hog,cnn}] [-n]
```

| Argument | Description |
|---|---|
| `source` | Folder containing the photos to scan |
| `dest` | Folder to copy photos with faces into. Defaults to `<source>/with_faces` |
| `-r`, `--recursive` | Also scan subfolders of the source |
| `-m`, `--model` | `hog` (default, faster on CPU) or `cnn` (more accurate, slow without a GPU) |
| `-n`, `--dry-run` | Detect faces and report results without creating folders or copying files |

### Examples

```
# Preview what would be copied
python filter.py "F:\Backup\backup\jpg" --dry-run

# Copy photos with faces to F:\Backup\backup\jpg\with_faces
python filter.py "F:\Backup\backup\jpg"

# Custom destination, including subfolders
python filter.py "F:\Backup\backup\jpg" "F:\Backup\faces" -r
```

## Behavior

- The destination folder is created if it doesn't exist.
- If the destination is inside the source, it is skipped when scanning, so re-runs don't pick up earlier copies.
- Existing files are never overwritten. A name clash is saved as `name_1.jpg`, `name_2.jpg`, and so on.
- Copies keep the original file timestamps.
- Unreadable or corrupt images are reported as `[ERROR]` and skipped.
- A summary of copied, skipped and errored files is printed at the end.

## Performance

Detection is the slow part: large photos can take several seconds each, so thousands of photos may take an hour or more. A dry run takes as long as a real run.
