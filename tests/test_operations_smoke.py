"""Smoke tests: run every operation against a synthetic image and check output shape/dtype."""

import numpy as np

from medical_image_gui import frequency_filters as ff
from medical_image_gui import spatial_filters as sf
from medical_image_gui import transformations as tr


def _make_gray(size: int = 64) -> np.ndarray:
    rng = np.random.default_rng(0)
    return rng.integers(0, 256, size=(size, size), dtype=np.uint8)


def _make_rgb(size: int = 64) -> np.ndarray:
    rng = np.random.default_rng(1)
    return rng.integers(0, 256, size=(size, size, 3), dtype=np.uint8)


def _check(out, ref):
    assert out.shape == ref.shape, (out.shape, ref.shape)
    assert out.dtype == np.uint8


def test_gray_level_transformations():
    for img in (_make_gray(), _make_rgb()):
        _check(tr.identity(img), img)
        _check(tr.negative(img), img)
        _check(tr.log_transform(img), img)
        _check(tr.gamma_transform(img, gamma=0.5), img)
        _check(tr.contrast_stretch(img, r1=50, r2=200), img)
        _check(tr.intensity_slicing(img, low=80, high=180), img)
        _check(tr.histogram_equalization(img), img)


def test_spatial_filters():
    for img in (_make_gray(), _make_rgb()):
        _check(sf.mean_filter(img, 3), img)
        _check(sf.gaussian_filter(img, 5, sigma=1.0), img)
        _check(sf.min_filter(img, 3), img)
        _check(sf.max_filter(img, 3), img)
        _check(sf.median_filter(img, 3), img)
        _check(sf.sobel_operator(img), img)
        _check(sf.prewitt_operator(img), img)
        _check(sf.laplacian_operator(img), img)


def test_frequency_filters():
    for img in (_make_gray(), _make_rgb()):
        _check(ff.ideal_lowpass(img, cutoff=10), img)
        _check(ff.butterworth_lowpass(img, cutoff=10, order=2), img)
        _check(ff.gaussian_lowpass(img, cutoff=10), img)
        _check(ff.ideal_highpass(img, cutoff=10), img)
        _check(ff.butterworth_highpass(img, cutoff=10, order=2), img)
        _check(ff.gaussian_highpass(img, cutoff=10), img)


if __name__ == "__main__":
    test_gray_level_transformations()
    test_spatial_filters()
    test_frequency_filters()
    print("All smoke tests passed.")
