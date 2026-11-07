"""Общий модуль тёмного стиля графиков «Тёмная обжарка» (стиль A).

Импортируется и в блокноте (stat-lab1-s2.ipynb), и в marimo-приложении
(marimo_generator.py), чтобы все графики выглядели единообразно: тёмный фон,
серифный шрифт, кремовый текст, тусклая сетка.
"""

import matplotlib.pyplot as plt

PALETTE = {  # базовая тёмная палитра — нейтральная тёмная (не коричневая)
    "bg": "#141418",
    "panel": "#1e1e24",
    "text": "#eceae6",
    "muted": "#9a97a0",
    "grid": "#30303a",
    "axis": "#6d6b75",
}

ACCENTS = {  # два акцента — по датасету
    "coffee": "#c8884a",  # кофейная лаба — янтарный
    "horeca": "#f2e14a",  # наш датасет — яркий жёлтый Starter
    "second": "#5cb5a6",  # вспомогательный бирюзовый (линии моделей)
}

LABELS = {  # русские подписи с единицами для наших величин
    "rating": "Рейтинг (балл, 0–5)",
    "reviews": "Число отзывов (шт.)",
    "log_reviews": "ln(число отзывов)",
}


def apply_dark_style(accent="horeca"):
    """Ставит matplotlib rcParams в тёмном стиле «Тёмная обжарка».

    Фон фигуры и осей — PALETTE["panel"]/PALETTE["bg"], шрифт с засечками
    (font.family="serif"), цвета текста/осей/сетки — из PALETTE, цикл цветов
    (prop_cycle) — выбранный акцент из ACCENTS + "second" + "muted".

    Возвращает dict с выбранными цветами (accent, second, muted и т.д.)
    для использования в коде построения графиков.
    """
    try:
        ip = get_ipython()  # noqa: F821
        ip.run_line_magic("config", "InlineBackend.figure_format = 'retina'")
        ip.run_line_magic(
            "config",
            "InlineBackend.print_figure_kwargs = {'facecolor': '#141418', 'bbox_inches': 'tight'}",
        )
    except Exception:
        pass

    accent_color = ACCENTS.get(accent, ACCENTS["horeca"])
    cycle_colors = [accent_color, ACCENTS["second"], PALETTE["muted"]]

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif"],
            "font.size": 13,
            "figure.facecolor": PALETTE["bg"],
            "figure.dpi": 120,
            "axes.facecolor": PALETTE["bg"],
            "savefig.facecolor": PALETTE["bg"],
            "text.color": PALETTE["text"],
            "axes.labelcolor": PALETTE["muted"],
            "axes.labelsize": 12,
            "axes.titlecolor": PALETTE["text"],
            "axes.titleweight": "bold",
            "axes.titlesize": 15,
            "axes.linewidth": 0.8,
            "axes.axisbelow": True,
            "xtick.color": PALETTE["muted"],
            "ytick.color": PALETTE["muted"],
            "axes.edgecolor": PALETTE["axis"],
            "grid.color": PALETTE["grid"],
            "grid.alpha": 1,
            "axes.grid": True,
            "axes.prop_cycle": plt.cycler(color=cycle_colors),
            "legend.facecolor": PALETTE["panel"],
            "legend.edgecolor": PALETTE["axis"],
            "legend.labelcolor": PALETTE["text"],
            "figure.figsize": (8, 5),
        }
    )

    return {
        "accent": accent_color,
        "second": ACCENTS["second"],
        "muted": PALETTE["muted"],
        "bg": PALETTE["bg"],
        "panel": PALETTE["panel"],
        "text": PALETTE["text"],
        "grid": PALETTE["grid"],
        "axis": PALETTE["axis"],
    }


def styled_fig(nrows=1, ncols=1, **kw):
    """Создаёт fig, axes в тёмном стиле (фон panel у фигуры и осей).

    Тонкая обёртка над plt.subplots: применяет единый figsize по умолчанию
    и аккуратные отступы (tight_layout), сохраняя тёмный фон фигуры/осей.
    """
    kw.setdefault("figsize", plt.rcParams.get("figure.figsize", (8, 5)))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, **kw)

    fig.patch.set_facecolor(PALETTE["bg"])
    for ax in (axes.flat if hasattr(axes, "flat") else [axes]):
        ax.set_facecolor(PALETTE["bg"])
        for spine in ax.spines.values():
            spine.set_color(PALETTE["axis"])
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=PALETTE["grid"], lw=0.7)
        ax.grid(axis="x", visible=False)
        ax.tick_params(length=0)

    fig.tight_layout()
    return fig, axes
