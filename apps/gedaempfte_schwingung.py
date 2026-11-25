# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "numpy",
#     "altair",
#     "wigglystuff",
# ]
#
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Gedämpfte Schwingung")


@app.cell(hide_code=True)
def _():
    import altair as alt
    import marimo as mo
    import numpy as np
    from wigglystuff import TangleLatex

    return TangleLatex, alt, mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Gedämpfte harmonische Schwingung

    Ziehen Sie an $\delta$ oder $\omega_0$ in der Bewegungsgleichung, um ihre Werte zu ändern. Anfangsbedingungen: $x(0) = x_A = 1$, $\dot x(0) = 0$.
    """)
    return


@app.cell(hide_code=True)
def _(TangleLatex, mo):
    formula = mo.ui.anywidget(
        TangleLatex(
            latex=r"\ddot x + 2\note{delta}{\tangle{delta}}\,\dot x + \note{omega0}{\tangle{omega0}}^2 x = 0",
            parameters={
                "delta": {
                    "value": 0.5, "min_value": 0.0, "max_value": 10.0, "step": 0.01, "pixels_per_step": 2,
                    "digits": 2, "display": "symbol", "symbol": r"\delta", "label": "Abklingkonstante δ",
                },
                "omega0": {
                    "value": 6.283185307179586, "min_value": 0.5, "max_value": 10.0, "step": 0.05,
                    "digits": 2, "display": "symbol", "symbol": r"\omega_0", "label": "Eigenkreisfrequenz ω₀",
                },
            },
            notes={
                "delta": r"Abklingkonstante $\delta = b/2m$",
                "omega0": r"Eigenkreisfrequenz $\omega_0 = \sqrt{D/m}$",
            },
            reveal_all_on_drag=True,
        )
    )
    return (formula,)


@app.cell(hide_code=True)
def _(mo):
    # Ändert der Button die Werte von Python aus, löst das keine Neuberechnung aus.
    get_tick, set_tick = mo.state(0)
    return get_tick, set_tick


@app.cell(hide_code=True)
def _(formula, mo, set_tick):
    def _grenzfall(_):
        formula.widget.values = {**formula.widget.values, "delta": formula.widget.values["omega0"]}
        set_tick(lambda n: n + 1)

    grenzfall_button = mo.ui.button(label="Grenzfall einstellen", on_click=_grenzfall)
    mo.vstack([formula, mo.hstack([grenzfall_button], justify="start")])
    return


@app.cell(hide_code=True)
def _(np):
    X_A = 1.0
    T_MAX = 6.0  # feste Zeitachse in s, damit die Fälle vergleichbar bleiben
    TOL = 1e-9

    def fall(delta, omega0):
        if abs(delta - omega0) < TOL:
            return "grenz"
        return "schwing" if delta < omega0 else "kriech"

    def auslenkung(delta, omega0, x_a=X_A):
        """Exakte Lösung x(t) als Vega-Ausdruck, damit der Browser die Kurve selbst berechnet."""
        t = "datum.t"
        match fall(delta, omega0):
            case "schwing":
                omega = np.sqrt(omega0**2 - delta**2)
                return f"{x_a} * exp({-delta} * {t}) * (cos({omega} * {t}) + {delta / omega} * sin({omega} * {t}))"
            case "grenz":
                return f"{x_a} * exp({-delta} * {t}) * (1 + {delta} * {t})"
            case _:
                root = np.sqrt(delta**2 - omega0**2)
                l1, l2 = -delta + root, -delta - root
                return f"{x_a} * ({l2} * exp({l1} * {t}) - {l1} * exp({l2} * {t})) / {l2 - l1}"

    return T_MAX, X_A, auslenkung, fall


@app.cell(hide_code=True)
def _(fall, formula, get_tick, mo, np):
    get_tick()
    delta, omega0 = formula.widget.values["delta"], formula.widget.values["omega0"]
    case = fall(delta, omega0)
    names = {"schwing": "Schwingfall", "grenz": "Aperiodischer Grenzfall", "kriech": "Kriechfall"}
    unit = r"\,\mathrm{s^{-1}}"
    parts = [
        rf"\delta = {delta:.3f}{unit}",
        rf"\omega_0 = {omega0:.3f}{unit}",
        rf"\delta/\omega_0 = {delta / omega0:.3f}",
    ]
    if case == "schwing":
        omega = np.sqrt(omega0**2 - delta**2)
        parts += [rf"\omega = {omega:.3f}{unit}", rf"T = 2\pi/\omega = {2 * np.pi / omega:.3f}\,\mathrm{{s}}"]
    mo.md(f"**{names[case]}**: $" + r",\quad ".join(parts) + "$")
    return case, delta, omega0


@app.cell(hide_code=True)
def _(T_MAX):
    # Merkt sich den gezoomten Ausschnitt, damit er beim Ändern der Parameter erhalten bleibt.
    # Bewusst kein mo.state: Das Zoomen selbst soll nichts neu berechnen.
    HOME = {"x": [0.0, T_MAX], "y": [-1.1, 1.1]}
    zoom_store = {"view": HOME}
    return HOME, zoom_store


@app.cell(hide_code=True)
def _(HOME, T_MAX, X_A, alt, auslenkung, case, delta, mo, omega0, zoom_store):
    ENV = "Einhüllende ±xₐe^(−δt)"
    curves = {"x": auslenkung(delta, omega0), "p": f"{X_A} * exp({-delta} * datum.t)", "m": "-datum.p"}
    # Python schickt nur die Formeln, die 600 Punkte pro Kurve berechnet der Browser.
    data = (
        alt.Chart(alt.sequence(0, T_MAX + 0.005, 0.01, as_="t"))
        .transform_calculate(**curves)
        .transform_fold(list(curves), as_=["Zweig", "x"])
        .transform_calculate(
            Kurve=f"datum.Zweig == 'x' ? 'x(t)' : '{ENV}'"
        )
    )

    zoom = alt.selection_interval(bind="scales", name="zoom", encodings=["x", "y"], value=zoom_store["view"])
    x_axis = alt.X("t:Q", title="Zeit t (s)", scale=alt.Scale(domain=HOME["x"], nice=False))
    y_axis = alt.Y("x:Q", title="Auslenkung x(t)", scale=alt.Scale(domain=HOME["y"], nice=False))
    # Außerhalb des Schwingfalls hüllt e^(−δt) keine Schwingung mehr ein, daher blasser.
    env_color = f"rgba(255, 127, 14, {1.0 if case == 'schwing' else 0.35})"
    colors = alt.Scale(
        domain=["x(t)", ENV],
        range=["#1f77b4", env_color],
    )
    lines = (
        data.mark_line(clip=True)
        .encode(
            x=x_axis, y=y_axis,
            color=alt.Color("Kurve:N", scale=colors, title=None,
                            legend=alt.Legend(orient="top-right", labelColor="#888888", labelFontSize=14, labelLimit=300)),
            detail="Zweig:N",
            strokeDash=alt.condition(f"datum.Kurve == '{ENV}'", alt.value([6, 4]), alt.value([1, 0])),
            strokeWidth=alt.condition("datum.Kurve == 'x(t)'", alt.value(3), alt.value(1.5)),
            tooltip=[alt.Tooltip("Kurve:N"), alt.Tooltip("t:Q", format=".3f"), alt.Tooltip("x:Q", format=".3f")],
        )
        .add_params(zoom)
    )
    # Achsen sitzen in Vega-Lite immer am Rand, daher markieren zwei Linien den Ursprung.
    origin = alt.Chart(alt.Data(values=[{"t": 0, "x": 0}])).mark_rule(color="rgba(128, 128, 128, 0.8)")
    axes_lines = [origin.encode(y="x:Q"), origin.encode(x="t:Q")]
    chart = (
        alt.layer(*axes_lines, lines)
        .properties(width="container", height=420)
        .configure(background="transparent")
        .configure_view(stroke=None)
        .configure_axis(labelFontSize=13, titleFontSize=14, gridColor="rgba(128, 128, 128, 0.2)", labelColor="#888888", titleColor="#888888", domainColor="#888888", tickColor="#888888")
    )

    def _store_zoom(_):
        # marimo meldet den Ausschnitt mit Feldnamen, Vega-Lite erwartet beim Start Kanalnamen.
        sel = plot.selections.get("zoom", {})
        if "t" in sel and "x" in sel:
            zoom_store["view"] = {"x": sel["t"], "y": sel["x"]}
        else:  # Doppelklick hat den Ausschnitt zurückgesetzt
            zoom_store["view"] = HOME

    plot = mo.ui.altair_chart(chart, chart_selection=False, legend_selection=False, on_change=_store_zoom)
    mo.vstack([
        plot,
        mo.md("Mit dem Mausrad zoomen, mit gedrückter Maustaste verschieben, Doppelklick setzt die Ansicht zurück.").style(
            font_size="0.85em", color="#888888"
        ),
    ])
    return (plot,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Die drei Fälle

    Der Ansatz $x(t) = e^{\lambda t}$ macht aus der Bewegungsgleichung $\lambda^2 + 2\delta\lambda + \omega_0^2 = 0$, also $\lambda = -\delta \pm \sqrt{\delta^2 - \omega_0^2}$. Das Vorzeichen unter der Wurzel bestimmt den Fall:

    - **Schwingfall** ($\delta < \omega_0$): Die Wurzel ist imaginär, $\lambda = -\delta \pm i\omega$ mit $\omega = \sqrt{\omega_0^2 - \delta^2}$. Daraus folgt $x(t) \approx x_A e^{-\delta t}\cos\omega t$: eine Schwingung, deren Amplitude mit der Rate $\delta$ abklingt. Wegen $\omega < \omega_0$ ist die Periode $T = 2\pi/\omega$ länger als ohne Dämpfung.
    - **Aperiodischer Grenzfall** ($\delta = \omega_0$): Die Wurzel verschwindet, beide Lösungen fallen zu $\lambda = -\delta$ zusammen, und die zweite Lösung ist $t\,e^{-\delta t}$. Mit den Anfangsbedingungen ergibt sich $x(t) = x_A e^{-\delta t}(1 + \delta t)$. Die Masse kehrt ohne Überschwingen mit der Rate $\omega_0$ in die Ruhelage zurück, schneller als in den beiden anderen Fällen.
    - **Kriechfall** ($\delta > \omega_0$): Beide $\lambda$ sind reell und negativ, es gibt keine Schwingung. Der langsamere Anteil klingt nur mit der Rate $\delta - \sqrt{\delta^2 - \omega_0^2} < \omega_0$ ab, sodass die Masse langsamer als im Grenzfall in die Ruhelage kriecht.

    Die Kurve im Diagramm ist die exakte Lösung für $x(0) = x_A$ und $\dot x(0) = 0$. Im Schwingfall weicht sie deshalb bei starker Dämpfung leicht von $x_A e^{-\delta t}\cos\omega t$ ab.
    """)
    return


if __name__ == "__main__":
    app.run()
