"""Tkinter GUI for medical image processing.

Run with:
    python -m medical_image_gui.app
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

import numpy as np
from PIL import Image, ImageTk

from . import frequency_filters as ff
from . import spatial_filters as sf
from . import transformations as tr

DISPLAY_MAX = 420  # max width/height for the on-screen image previews


# Each entry: (label, callable(image, params_dict) -> np.ndarray, params_spec)
# params_spec is a list of (name, kind, default, options/range)
OPERATIONS: dict[str, dict] = {
    # --- Gray-level transformations ---
    "Identity Transformation": {
        "fn": lambda img, p: tr.identity(img),
        "params": [],
        "group": "Gray Level Transformations",
    },
    "Negative Transformation": {
        "fn": lambda img, p: tr.negative(img),
        "params": [],
        "group": "Gray Level Transformations",
    },
    "Log Transformation": {
        "fn": lambda img, p: tr.log_transform(img),
        "params": [],
        "group": "Gray Level Transformations",
    },
    "Power-Law (Gamma) Transformation": {
        "fn": lambda img, p: tr.gamma_transform(img, gamma=float(p.get("gamma", 1.0))),
        "params": [("gamma", "float", 0.5, (0.05, 5.0))],
        "group": "Gray Level Transformations",
    },
    "Contrast Stretching": {
        "fn": lambda img, p: tr.contrast_stretch(
            img,
            r1=float(p.get("r1", 50)),
            r2=float(p.get("r2", 200)),
        ),
        "params": [
            ("r1", "int", 50, (0, 255)),
            ("r2", "int", 200, (0, 255)),
        ],
        "group": "Gray Level Transformations",
    },
    "Intensity Slicing": {
        "fn": lambda img, p: tr.intensity_slicing(
            img,
            low=int(p.get("low", 100)),
            high=int(p.get("high", 200)),
            preserve_background=bool(p.get("preserve", False)),
        ),
        "params": [
            ("low", "int", 100, (0, 255)),
            ("high", "int", 200, (0, 255)),
            ("preserve", "bool", False, None),
        ],
        "group": "Gray Level Transformations",
    },
    "Histogram Processing": {
        "fn": lambda img, p: img,  # display only; histogram window is opened separately
        "params": [],
        "group": "Gray Level Transformations",
        "show_histogram": True,
    },
    "Histogram Equalization": {
        "fn": lambda img, p: tr.histogram_equalization(img),
        "params": [],
        "group": "Gray Level Transformations",
        "show_histogram": True,
    },
    # --- Spatial-domain filters ---
    "Mean Filter": {
        "fn": lambda img, p: sf.mean_filter(img, ksize=int(p.get("ksize", 3))),
        "params": [("ksize", "int", 3, (3, 15))],
        "group": "Spatial Domain Filters",
    },
    "Gaussian Filter": {
        "fn": lambda img, p: sf.gaussian_filter(
            img, ksize=int(p.get("ksize", 5)), sigma=float(p.get("sigma", 1.0))
        ),
        "params": [("ksize", "int", 5, (3, 15)), ("sigma", "float", 1.0, (0.1, 10.0))],
        "group": "Spatial Domain Filters",
    },
    "Min Filter": {
        "fn": lambda img, p: sf.min_filter(img, ksize=int(p.get("ksize", 3))),
        "params": [("ksize", "int", 3, (3, 15))],
        "group": "Spatial Domain Filters",
    },
    "Max Filter": {
        "fn": lambda img, p: sf.max_filter(img, ksize=int(p.get("ksize", 3))),
        "params": [("ksize", "int", 3, (3, 15))],
        "group": "Spatial Domain Filters",
    },
    "Median Filter": {
        "fn": lambda img, p: sf.median_filter(img, ksize=int(p.get("ksize", 3))),
        "params": [("ksize", "int", 3, (3, 15))],
        "group": "Spatial Domain Filters",
    },
    "Sobel Operator": {
        "fn": lambda img, p: sf.sobel_operator(img),
        "params": [],
        "group": "Spatial Domain Filters",
    },
    "Prewitt Operator": {
        "fn": lambda img, p: sf.prewitt_operator(img),
        "params": [],
        "group": "Spatial Domain Filters",
    },
    "Laplacian Operator": {
        "fn": lambda img, p: sf.laplacian_operator(img),
        "params": [],
        "group": "Spatial Domain Filters",
    },
    # --- Frequency-domain filters ---
    "Ideal Low Pass Filter": {
        "fn": lambda img, p: ff.ideal_lowpass(img, cutoff=float(p.get("cutoff", 30))),
        "params": [("cutoff", "float", 30.0, (1.0, 300.0))],
        "group": "Frequency Domain Filters",
    },
    "Butterworth Low Pass Filter": {
        "fn": lambda img, p: ff.butterworth_lowpass(
            img, cutoff=float(p.get("cutoff", 30)), order=int(p.get("order", 2))
        ),
        "params": [("cutoff", "float", 30.0, (1.0, 300.0)), ("order", "int", 2, (1, 10))],
        "group": "Frequency Domain Filters",
    },
    "Gaussian Low Pass Filter": {
        "fn": lambda img, p: ff.gaussian_lowpass(img, cutoff=float(p.get("cutoff", 30))),
        "params": [("cutoff", "float", 30.0, (1.0, 300.0))],
        "group": "Frequency Domain Filters",
    },
    "Ideal High Pass Filter": {
        "fn": lambda img, p: ff.ideal_highpass(img, cutoff=float(p.get("cutoff", 30))),
        "params": [("cutoff", "float", 30.0, (1.0, 300.0))],
        "group": "Frequency Domain Filters",
    },
    "Butterworth High Pass Filter": {
        "fn": lambda img, p: ff.butterworth_highpass(
            img, cutoff=float(p.get("cutoff", 30)), order=int(p.get("order", 2))
        ),
        "params": [("cutoff", "float", 30.0, (1.0, 300.0)), ("order", "int", 2, (1, 10))],
        "group": "Frequency Domain Filters",
    },
    "Gaussian High Pass Filter": {
        "fn": lambda img, p: ff.gaussian_highpass(img, cutoff=float(p.get("cutoff", 30))),
        "params": [("cutoff", "float", 30.0, (1.0, 300.0))],
        "group": "Frequency Domain Filters",
    },
}


def _grouped_operation_labels() -> list[str]:
    """Return operation names with group separators inserted (non-selectable visually)."""
    groups: dict[str, list[str]] = {}
    for name, spec in OPERATIONS.items():
        groups.setdefault(spec["group"], []).append(name)
    out: list[str] = []
    for group, names in groups.items():
        out.append(f"── {group} ──")
        out.extend(names)
    return out


def _array_to_photoimage(arr: np.ndarray, max_side: int = DISPLAY_MAX) -> ImageTk.PhotoImage:
    img = Image.fromarray(arr)
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


class MedicalImageApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Medical Image Processing — FMI Assignment")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self.original_array: np.ndarray | None = None
        self.processed_array: np.ndarray | None = None
        self._original_photo: ImageTk.PhotoImage | None = None
        self._processed_photo: ImageTk.PhotoImage | None = None
        self._param_widgets: dict[str, tk.Variable] = {}

        self._build_controls()
        self._build_displays()
        self._build_statusbar()
        self._populate_param_panel()

    # ---- layout ------------------------------------------------------------

    def _build_controls(self) -> None:
        bar = ttk.Frame(self, padding=8)
        bar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(bar, text="Upload Image", command=self.on_upload).pack(side=tk.LEFT)

        ttk.Label(bar, text="Operation:").pack(side=tk.LEFT, padx=(12, 4))
        self.op_var = tk.StringVar(value="Identity Transformation")
        self.op_combo = ttk.Combobox(
            bar,
            textvariable=self.op_var,
            values=_grouped_operation_labels(),
            state="readonly",
            width=38,
        )
        self.op_combo.pack(side=tk.LEFT)
        self.op_combo.bind("<<ComboboxSelected>>", self._on_operation_change)

        ttk.Button(bar, text="Apply", command=self.on_apply).pack(side=tk.LEFT, padx=8)
        ttk.Button(bar, text="Save Result…", command=self.on_save).pack(side=tk.LEFT)
        ttk.Button(bar, text="Show Histograms", command=self.show_histograms).pack(
            side=tk.LEFT, padx=8
        )

        # Parameter panel (right side of controls)
        self.param_frame = ttk.LabelFrame(self, text="Parameters", padding=8)
        self.param_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(0, 6))

    def _build_displays(self) -> None:
        body = ttk.Frame(self, padding=8)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        left = ttk.LabelFrame(body, text="Original")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        self.original_label = ttk.Label(left, anchor="center")
        self.original_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        right = ttk.LabelFrame(body, text="Processed")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))
        self.processed_label = ttk.Label(right, anchor="center")
        self.processed_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _build_statusbar(self) -> None:
        self.status_var = tk.StringVar(value="Load an image to begin.")
        ttk.Label(self, textvariable=self.status_var, anchor="w", relief=tk.SUNKEN).pack(
            side=tk.BOTTOM, fill=tk.X
        )

    # ---- parameter panel ---------------------------------------------------

    def _populate_param_panel(self) -> None:
        for child in self.param_frame.winfo_children():
            child.destroy()
        self._param_widgets.clear()

        op_name = self.op_var.get()
        spec = OPERATIONS.get(op_name)
        if not spec or not spec["params"]:
            ttk.Label(self.param_frame, text="(no parameters)").pack(side=tk.LEFT)
            return

        for name, kind, default, rng in spec["params"]:
            container = ttk.Frame(self.param_frame)
            container.pack(side=tk.LEFT, padx=6)
            ttk.Label(container, text=f"{name}:").pack(side=tk.LEFT)
            if kind == "bool":
                var = tk.BooleanVar(value=bool(default))
                ttk.Checkbutton(container, variable=var).pack(side=tk.LEFT)
            elif kind == "int":
                var = tk.IntVar(value=int(default))
                ttk.Spinbox(
                    container,
                    from_=rng[0],
                    to=rng[1],
                    textvariable=var,
                    width=6,
                    increment=1,
                ).pack(side=tk.LEFT)
            else:  # float
                var = tk.DoubleVar(value=float(default))
                ttk.Spinbox(
                    container,
                    from_=rng[0],
                    to=rng[1],
                    textvariable=var,
                    width=8,
                    increment=0.1,
                ).pack(side=tk.LEFT)
            self._param_widgets[name] = var

    def _on_operation_change(self, _event=None) -> None:
        # Skip group separators
        if self.op_var.get().startswith("──"):
            # find next real operation
            for op in OPERATIONS:
                self.op_var.set(op)
                break
        self._populate_param_panel()

    def _collect_params(self) -> dict:
        return {name: var.get() for name, var in self._param_widgets.items()}

    # ---- handlers ----------------------------------------------------------

    def on_upload(self) -> None:
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            pil = Image.open(path)
            if pil.mode not in ("L", "RGB"):
                pil = pil.convert("RGB")
            self.original_array = np.array(pil)
            self.processed_array = None
            self._show_image(self.original_label, self.original_array, slot="original")
            self.processed_label.configure(image="")
            self._processed_photo = None
            self.status_var.set(
                f"Loaded {path} — shape={self.original_array.shape}, dtype={self.original_array.dtype}"
            )
        except Exception as exc:  # noqa: BLE001 — surface to user
            messagebox.showerror("Failed to load image", str(exc))

    def on_apply(self) -> None:
        if self.original_array is None:
            messagebox.showinfo("No image", "Please upload an image first.")
            return
        op_name = self.op_var.get()
        spec = OPERATIONS.get(op_name)
        if not spec or op_name.startswith("──"):
            messagebox.showinfo("Choose an operation", "Please select a valid operation.")
            return
        try:
            params = self._collect_params()
            self.status_var.set(f"Applying {op_name}…")
            self.update_idletasks()
            self.processed_array = spec["fn"](self.original_array, params)
            self._show_image(self.processed_label, self.processed_array, slot="processed")
            self.status_var.set(f"Done: {op_name}")
            if spec.get("show_histogram"):
                self.show_histograms()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Operation failed", str(exc))
            self.status_var.set("Error.")

    def on_save(self) -> None:
        if self.processed_array is None:
            messagebox.showinfo("Nothing to save", "Apply an operation first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")],
        )
        if not path:
            return
        try:
            Image.fromarray(self.processed_array).save(path)
            self.status_var.set(f"Saved processed image to {path}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Failed to save", str(exc))

    # ---- helpers -----------------------------------------------------------

    def _show_image(self, label: ttk.Label, arr: np.ndarray, slot: str) -> None:
        photo = _array_to_photoimage(arr)
        label.configure(image=photo)
        if slot == "original":
            self._original_photo = photo
        else:
            self._processed_photo = photo

    def show_histograms(self) -> None:
        if self.original_array is None:
            messagebox.showinfo("No image", "Please upload an image first.")
            return
        try:
            import matplotlib.pyplot as plt  # imported lazily
        except ImportError:
            messagebox.showerror(
                "Matplotlib missing",
                "matplotlib is required for histogram display. Install it via\n\n"
                "    pip install matplotlib",
            )
            return

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].set_title("Original histogram")
        axes[0].bar(range(256), tr.compute_histogram(self.original_array), width=1.0)
        axes[0].set_xlim(0, 255)

        if self.processed_array is not None:
            axes[1].set_title("Processed histogram")
            axes[1].bar(range(256), tr.compute_histogram(self.processed_array), width=1.0)
        else:
            axes[1].set_title("(no processed image yet)")
        axes[1].set_xlim(0, 255)

        fig.tight_layout()
        plt.show()


def main() -> None:
    app = MedicalImageApp()
    app.mainloop()


if __name__ == "__main__":
    main()
