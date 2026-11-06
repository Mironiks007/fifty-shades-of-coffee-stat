"""Общий модуль тёмного стиля графиков «Тёмная обжарка» (стиль A).

Импортируется и в блокноте (stat-lab1-s2.ipynb), и в marimo-приложении
(marimo_generator.py), чтобы все графики выглядели единообразно: тёмный фон,
серифный шрифт, кремовый текст, тусклая сетка.
"""

import matplotlib.pyplot as plt

PALETTE = {  # базовая тёмная палитра «Тёмная обжарка»
    "bg": "#1b1310",
    "panel": "#241914",
    "text": "#ece0d0",
    "muted": "#b59a86",
    "grid": "#3a2a22",
    "axis": "#9a8574",
}

ACCENTS = {  # два акцента — по датасету
    "coffee": "#c8884a",  # кофейная лаба — янтарный
    "horeca": "#e8c84a",  # наш датасет — жёлтый Starter (тёплый золотой)
    "second": "#7fae9b",  # вспомогательный бирюзовый (линии моделей)
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
    accent_color = ACCENTS.get(accent, ACCENTS["horeca"])
    cycle_colors = [accent_color, ACCENTS["second"], PALETTE["muted"]]

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif"],
            "figure.facecolor": PALETTE["bg"],
            "axes.facecolor": PALETTE["panel"],
            "savefig.facecolor": PALETTE["bg"],
            "text.color": PALETTE["text"],
            "axes.labelcolor": PALETTE["text"],
            "axes.titlecolor": PALETTE["text"],
            "xtick.color": PALETTE["muted"],
            "ytick.color": PALETTE["muted"],
            "axes.edgecolor": PALETTE["axis"],
            "grid.color": PALETTE["grid"],
            "grid.alpha": 0.6,
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
        ax.set_facecolor(PALETTE["panel"])
        for spine in ax.spines.values():
            spine.set_color(PALETTE["axis"])

    fig.tight_layout()
    return fig, axes
