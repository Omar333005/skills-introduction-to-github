"""Frequency-domain filters using the 2-D FFT."""

from __future__ import annotations

import numpy as np


def _to_uint8(arr: np.ndarray) -> np.ndarray:
    return np.clip(arr, 0, 255).astype(np.uint8)


def _distance_grid(shape: tuple[int, int]) -> np.ndarray:
    rows, cols = shape
    cy, cx = rows // 2, cols // 2
    y, x = np.ogrid[:rows, :cols]
    return np.sqrt((y - cy) ** 2 + (x - cx) ** 2)


def _apply_mask(channel: np.ndarray, mask: np.ndarray) -> np.ndarray:
    F = np.fft.fftshift(np.fft.fft2(channel.astype(np.float64)))
    G = F * mask
    g = np.real(np.fft.ifft2(np.fft.ifftshift(G)))
    g_min, g_max = g.min(), g.max()
    if g_max - g_min < 1e-9:
        return _to_uint8(g)
    g = (g - g_min) * 255.0 / (g_max - g_min)
    return _to_uint8(g)


def _apply_filter(image: np.ndarray, mask_fn) -> np.ndarray:
    if image.ndim == 2:
        mask = mask_fn(image.shape)
        return _apply_mask(image, mask)
    out = np.zeros_like(image)
    mask = mask_fn(image.shape[:2])
    for c in range(image.shape[2]):
        out[..., c] = _apply_mask(image[..., c], mask)
    return out


# --- Low pass filters --------------------------------------------------------

def ideal_lowpass(image: np.ndarray, cutoff: float = 30.0) -> np.ndarray:
    def mask(shape):
        return (_distance_grid(shape) <= cutoff).astype(np.float64)
    return _apply_filter(image, mask)


def butterworth_lowpass(image: np.ndarray, cutoff: float = 30.0, order: int = 2) -> np.ndarray:
    def mask(shape):
        d = _distance_grid(shape)
        return 1.0 / (1.0 + (d / max(cutoff, 1e-6)) ** (2 * order))
    return _apply_filter(image, mask)


def gaussian_lowpass(image: np.ndarray, cutoff: float = 30.0) -> np.ndarray:
    def mask(shape):
        d = _distance_grid(shape)
        return np.exp(-(d**2) / (2.0 * cutoff**2))
    return _apply_filter(image, mask)


# --- High pass filters -------------------------------------------------------

def ideal_highpass(image: np.ndarray, cutoff: float = 30.0) -> np.ndarray:
    def mask(shape):
        return (_distance_grid(shape) > cutoff).astype(np.float64)
    return _apply_filter(image, mask)


def butterworth_highpass(image: np.ndarray, cutoff: float = 30.0, order: int = 2) -> np.ndarray:
    def mask(shape):
        d = _distance_grid(shape)
        return 1.0 / (1.0 + (max(cutoff, 1e-6) / np.where(d == 0, 1e-6, d)) ** (2 * order))
    return _apply_filter(image, mask)


def gaussian_highpass(image: np.ndarray, cutoff: float = 30.0) -> np.ndarray:
    def mask(shape):
        d = _distance_grid(shape)
        return 1.0 - np.exp(-(d**2) / (2.0 * cutoff**2))
    return _apply_filter(image, mask)
