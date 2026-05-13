"""Spatial-domain filters implemented with NumPy (no OpenCV dependency)."""

from __future__ import annotations

import numpy as np


def _pad(image: np.ndarray, pad: int) -> np.ndarray:
    if image.ndim == 2:
        return np.pad(image, pad, mode="edge")
    return np.pad(image, ((pad, pad), (pad, pad), (0, 0)), mode="edge")


def _apply_per_channel(image: np.ndarray, fn) -> np.ndarray:
    if image.ndim == 2:
        return fn(image)
    out = np.zeros_like(image)
    for c in range(image.shape[2]):
        out[..., c] = fn(image[..., c])
    return out


def _convolve2d(channel: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(channel.astype(np.float64), ((pad_h, pad_h), (pad_w, pad_w)), mode="edge")

    # Build a strided view for vectorized convolution
    H, W = channel.shape
    shape = (H, W, kh, kw)
    strides = padded.strides * 2
    windows = np.lib.stride_tricks.as_strided(padded, shape=shape, strides=strides)
    return np.einsum("ijkl,kl->ij", windows, kernel)


def _windowed_stat(channel: np.ndarray, ksize: int, op) -> np.ndarray:
    pad = ksize // 2
    padded = np.pad(channel.astype(np.float64), ((pad, pad), (pad, pad)), mode="edge")
    H, W = channel.shape
    shape = (H, W, ksize, ksize)
    strides = padded.strides * 2
    windows = np.lib.stride_tricks.as_strided(padded, shape=shape, strides=strides)
    return op(windows.reshape(H, W, -1), axis=-1)


def _to_uint8(arr: np.ndarray) -> np.ndarray:
    return np.clip(arr, 0, 255).astype(np.uint8)


def mean_filter(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    kernel = np.ones((ksize, ksize), dtype=np.float64) / (ksize * ksize)
    return _apply_per_channel(image, lambda ch: _to_uint8(_convolve2d(ch, kernel)))


def gaussian_filter(image: np.ndarray, ksize: int = 5, sigma: float = 1.0) -> np.ndarray:
    ax = np.arange(ksize) - ksize // 2
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    kernel /= kernel.sum()
    return _apply_per_channel(image, lambda ch: _to_uint8(_convolve2d(ch, kernel)))


def min_filter(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    return _apply_per_channel(image, lambda ch: _to_uint8(_windowed_stat(ch, ksize, np.min)))


def max_filter(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    return _apply_per_channel(image, lambda ch: _to_uint8(_windowed_stat(ch, ksize, np.max)))


def median_filter(image: np.ndarray, ksize: int = 3) -> np.ndarray:
    return _apply_per_channel(image, lambda ch: _to_uint8(_windowed_stat(ch, ksize, np.median)))


def _gradient_magnitude(channel: np.ndarray, kx: np.ndarray, ky: np.ndarray) -> np.ndarray:
    gx = _convolve2d(channel, kx)
    gy = _convolve2d(channel, ky)
    mag = np.sqrt(gx**2 + gy**2)
    if mag.max() > 0:
        mag = mag * 255.0 / mag.max()
    return _to_uint8(mag)


def sobel_operator(image: np.ndarray) -> np.ndarray:
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)
    return _apply_per_channel(image, lambda ch: _gradient_magnitude(ch, kx, ky))


def prewitt_operator(image: np.ndarray) -> np.ndarray:
    kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float64)
    ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float64)
    return _apply_per_channel(image, lambda ch: _gradient_magnitude(ch, kx, ky))


def laplacian_operator(image: np.ndarray) -> np.ndarray:
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float64)

    def _laplace(channel: np.ndarray) -> np.ndarray:
        out = _convolve2d(channel, kernel)
        out = np.abs(out)
        if out.max() > 0:
            out = out * 255.0 / out.max()
        return _to_uint8(out)

    return _apply_per_channel(image, _laplace)
