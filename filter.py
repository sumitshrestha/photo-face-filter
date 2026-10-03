import argparse
import shutil
import sys
from pathlib import Path

import face_recognition

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Copy photos that contain at least one face from a source folder to a destination folder."
    )
    parser.add_argument("source", type=Path, help="Folder containing the photos to scan")
    parser.add_argument(
        "dest", type=Path, nargs="?",
        help="Folder to copy photos with faces into (default: <source>/with_faces)",
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true",
        help="Detect faces and report results without creating folders or copying files",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Scan subfolders of the source folder too"
    )
    parser.add_argument(
        "-m", "--model", choices=["hog", "cnn"], default="hog",
        help="Face detection model: 'hog' is faster on CPU, 'cnn' is more accurate (default: hog)",
    )
    return parser.parse_args()


def has_face(path, model):
    image = face_recognition.load_image_file(path)
    return len(face_recognition.face_locations(image, model=model)) > 0


def unique_destination(dest_dir, name):
    """Return a path in dest_dir that doesn't overwrite an existing file."""
    target = dest_dir / name
    stem, suffix = target.stem, target.suffix
    counter = 1
    while target.exists():
        target = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    return target


def main():
    args = parse_args()
    source = args.source.resolve()
    dest = (args.dest or source / "with_faces").resolve()

    if not source.is_dir():
        sys.exit(f"Source folder not found: {source}")
    if source == dest:
        sys.exit("Source and destination folders must be different.")

    if not args.dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    files = source.rglob("*") if args.recursive else source.iterdir()
    photos = sorted(
        p for p in files
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS and dest not in p.parents
    )

    copied = skipped = errors = 0
    for path in photos:
        try:
            if has_face(path, args.model):
                if not args.dry_run:
                    shutil.copy2(path, unique_destination(dest, path.name))
                copied += 1
                print(f"[FACE FOUND] {'Would copy' if args.dry_run else 'Copied'} {path.name}")
            else:
                skipped += 1
                print(f"[NO FACE] Skipped {path.name}")
        except Exception as e:
            errors += 1
            print(f"[ERROR] {path.name}: {e}")

    print(f"\nDone. {copied} copied, {skipped} without faces, {errors} errors (of {len(photos)} photos).")


if __name__ == "__main__":
    main()
