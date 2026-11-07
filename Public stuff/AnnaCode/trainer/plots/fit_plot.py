from collections import deque
from pyscript.js_modules import Plotly

from plot_utils import to_js

DATA_TRACE_COLORS = ["#17e262", '#0891b2', "#99c2ae", '#84cc16', '#14b8a6', '#65a30d']
LIVE_TRACE_COLORS = ['#f59e0b', '#ec4899', '#f97316', '#eab308', '#fb7185', '#fbbf24']
FIT_TRACE_COLORS = ['#0b7a3b', '#075985', '#5b7f6e', '#4d7c0f', '#0f766e', '#3f6212']   # darker than the data dots

TRACES_PER_OUTPUT = 3   # data dots, live dots, fit line (in that order)

class FitPlot:
    """Fit graph for dataset-based training, x-axis fixed to the FIRST
    input. Each OUTPUT gets its own set of three traces:
      Fit trace (line)     -- the network's own answer for that output swept across the
                               first input (other inputs held at their averages), redrawn
                               whenever the weights or data change (see
                               dataset_ui.refresh_fit_line_if_changed). A well-trained
                               network's line runs through the data dots.
      Data trace (markers) -- that output's raw (first-input x, y) dataset
                               points, set whenever the dataset table
                               changes.
      Live trace (markers) -- that output's ACTUAL live (input, output)
                               pairs, sampled once per forward() tick
                               while Play is running -- not a synthetic
                               sweep -- so what's drawn is a true
                               reflection of what the running network
                               produces, comparable against the Data trace.
    Trace sets are appended/removed dynamically as outputs are added to
    or removed from the network (see add_output_trace/remove_output_trace)."""

    def __init__(self, id, max_run_points=500):
        self.id = id
        self.max_run_points = max_run_points
        self.output_order = []   # oid, in trace-append order; oid's traces are at 3*pos (data), 3*pos+1 (live), 3*pos+2 (fit)
        self.run_data = {}       # oid -> {"xs": deque, "ys": deque}
        layout = to_js({
            "margin": {"l": 36, "r": 14, "t": 10, "b": 30},
            "xaxis": {"tickfont": {"size": 10}, "zeroline": True},
            "yaxis": {"tickfont": {"size": 10}, "autorange": True, "zeroline": True},
            "showlegend": True,
            "legend": {"font": {"size": 10}, "x": 0, "y": 1}
        })
        Plotly.newPlot(self.id, to_js([]), layout)

    def _pos(self, oid):
        return self.output_order.index(oid)

    def _trace(self, oid, kind):
        """Plotly trace index of an output's 'data', 'live' or 'fit' trace."""
        return self._pos(oid) * TRACES_PER_OUTPUT + ("data", "live", "fit").index(kind)

    def add_output_trace(self, oid, label=None):
        if oid in self.output_order:
            return
        pos = len(self.output_order)
        color = DATA_TRACE_COLORS[pos % len(DATA_TRACE_COLORS)]
        live_color = LIVE_TRACE_COLORS[pos % len(LIVE_TRACE_COLORS)]
        fit_color = FIT_TRACE_COLORS[pos % len(FIT_TRACE_COLORS)]
        name = label or f"y{pos + 1}"
        data_trace = {'x': [], 'y': [], 'mode': 'markers', 'type': 'scatter',
                      'name': f'{name} data', 'marker': {'color': color, 'size': 9}}
        live_trace = {'x': [], 'y': [], 'mode': 'markers', 'type': 'scatter',
                      'name': f'{name} live', 'marker': {'color': live_color, 'size': 6, 'opacity': 0.75}}
        fit_trace = {'x': [], 'y': [], 'mode': 'lines', 'type': 'scatter', 'hoverinfo': 'skip',
                     'name': f'{name} fit', 'line': {'color': fit_color, 'width': 3}}
        Plotly.addTraces(self.id, to_js([data_trace, live_trace, fit_trace]))
        self.output_order.append(oid)
        self.run_data[oid] = {"xs": deque([], self.max_run_points), "ys": deque([], self.max_run_points)}

    def remove_output_trace(self, oid):
        if oid not in self.output_order:
            return
        pos = self._pos(oid)
        first = pos * TRACES_PER_OUTPUT
        Plotly.deleteTraces(self.id, to_js(list(range(first, first + TRACES_PER_OUTPUT))))
        self.output_order.pop(pos)
        self.run_data.pop(oid, None)

    def update_data_points(self, oid, xs, ys):
        if oid not in self.output_order:
            return
        Plotly.restyle(self.id, to_js({'x': [list(xs)], 'y': [list(ys)]}),
                        to_js([self._trace(oid, "data")]))

    def update_fit(self, oid, xs, ys):
        """Redraw an output's fit line."""
        if oid not in self.output_order:
            return
        Plotly.restyle(self.id, to_js({'x': [list(xs)], 'y': [list(ys)]}),
                        to_js([self._trace(oid, "fit")]))

    def reset_run(self):
        for oid in self.output_order:
            rd = self.run_data[oid]
            rd["xs"].clear()
            rd["ys"].clear()
            Plotly.restyle(self.id, to_js({'x': [[]], 'y': [[]]}),
                            to_js([self._trace(oid, "live")]))

    def add_run_point(self, oid, x, y):
        rd = self.run_data.get(oid)
        if rd is None:
            return
        rd["xs"].append(x)
        rd["ys"].append(y)
        Plotly.restyle(self.id, to_js(
            {'x': [list(rd["xs"])], 'y': [list(rd["ys"])]}), to_js([self._trace(oid, "live")]))
