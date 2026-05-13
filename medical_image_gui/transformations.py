"""Gray-level intensity transformations.

All functions accept a NumPy array (grayscale or RGB) and return a uint8 array.
Color images are processed per channel where it makes sense.
"""

from __future__ import annotations

import numpy as np


def _as_float(image: np.ndarray) -> np.ndarray:
    return image.astype(np.float64)


def _to_uint8(image: np.ndarray) -> np.ndarray:
    return np.clip(image, 0, 255).astype(np.uint8)


def identity(image: np.ndarray) -> np.ndarray:
    return image.copy()


def negative(image: np.ndarray) -> np.ndarray:
    return _to_uint8(255.0 - _as_float(image))


def log_transform(image: np.ndarray, c: float | None = None) -> np.ndarray:
    f = _as_float(image)
    if c is None:
        c = 255.0 / np.log1p(f.max() if f.max() > 0 else 1.0)
    return _to_uint8(c * np.log1p(f))


def gamma_transform(image: np.ndarray, gamma: float = 1.0, c: float = 1.0) -> np.ndarray:
    f = _as_float(image) / 255.0
    out = c * np.power(f, gamma) * 255.0
    return _to_uint8(out)


def contrast_stretch(
    image: np.ndarray,
    r1: float | None = None,
    r2: float | None = None,
    s1: float = 0.0,
    s2: float = 255.0,
) -> np.ndarray:
    f = _as_float(image)
    if r1 is None:
        r1 = float(f.min())
    if r2 is None:
        r2 = float(f.max())
    if r2 - r1 < 1e-6:
        return _to_uint8(f)

    out = np.where(
        f <= r1,
        s1 * (f / max(r1, 1e-6)),
        np.where(
            f <= r2,
            s1 + (s2 - s1) * (f - r1) / (r2 - r1),
            s2 + (255.0 - s2) * (f - r2) / max(255.0 - r2, 1e-6),
        ),
    )
    return _to_uint8(out)


def intensity_slicing(
    image: np.ndarray,
    low: int = 100,
    high: int = 200,
    preserve_background: bool = False,
    highlight: int = 255,
) -> np.ndarray:
    f = _as_float(image)
    in_range = (f >= low) & (f <= high)
    if preserve_background:
        out = np.where(in_range, highlight, f)
    else:
        out = np.where(in_range, highlight, 0)
    return _to_uint8(out)


def _equalize_channel(channel: np.ndarray) -> np.ndarray:
    hist, _ = np.histogram(channel.flatten(), bins=256, range=(0, 256))
    cdf = hist.cumsum()
    cdf_masked = np.ma.masked_equal(cdf, 0)
    cdf_min = cdf_masked.min()
    total = cdf_masked.max() - cdf_min
    if total == 0:
        return channel
    cdf_scaled = (cdf_masked - cdf_min) * 255.0 / total
    lut = np.ma.filled(cdf_scaled, 0).astype(np.uint8)
    return lut[channel]


def histogram_equalization(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return _equalize_channel(image)
    out = np.zeros_like(image)
    for c in range(image.shape[2]):
        out[..., c] = _equalize_channel(image[..., c])
    return out


def compute_histogram(image: np.ndarray) -> np.ndarray:
    """Return histogram counts (256 bins) for a grayscale view of the image."""
    if image.ndim == 3:
        # Convert to luminance for histogram display
        gray = (0.299 * image[..., 0] + 0.587 * image[..., 1] + 0.114 * image[..., 2]).astype(np.uint8)
    else:
        gray = image
    hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
    return hist
