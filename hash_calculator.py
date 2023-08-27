from binascii import crc32
from hashlib import md5, sha1


def compute_hashes(file_path):
    """Compute CRC32, MD5, and SHA1 hashes for a given file."""
    with open(file_path, 'rb') as f:
        shasum = sha1()
        md5sum = md5()
        crcsum = 0

        chunk = f.read(4096)
        while chunk:
            shasum.update(chunk)
            md5sum.update(chunk)
            crcsum = crc32(chunk, crcsum)
            chunk = f.read(4096)

    return {
        "crc32": format(crcsum & 0xFFFFFFFF, '08x'),
        "md5": md5sum.hexdigest(),
        "sha1": shasum.hexdigest()
    }

