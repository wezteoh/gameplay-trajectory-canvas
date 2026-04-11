from typing import Literal

import matplotlib.lines as lines
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from imageio import mimsave
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection

"""
This is a modified version of the mplbasketball library.
https://github.com/jason-zheng/mplbasketball
"""

# Feet of margin around court limits in matplotlib renders (tighter than library default 5).
COURT_PAD_FT = 2.0
# Reference + preview use the same court framing as the drawable canvas (court_image).
STATIC_VIEW_PAD_FT = COURT_PAD_FT
# DPI for reference + conditioning preview in the Streamlit UI.
STATIC_VIEW_DPI = 96

nba_court_parameters = {
    "court_dims": [94.0, 50.0],
    # Hoop area
    "hoop_distance_from_edge": 5.25,
    "hoop_radius": 0.75,
    # backboard parameters
    "backboard_distance_from_edge": 4.0,
    "backboard_width": 6.0,
    "backboard_height": 3.5,
    "backboard_inner_rect_width": 2.0,
    "backboard_inner_rect_height": 1.5,
    "backboard_inner_rect_from_bottom": 1.0,
    "charge_circle_radius": 4.0,
    "charge_circle_side_length": 3.0,
    # Inbound lines
    "inbound_line_distance_from_edge": 28.0,
    "inbound_line_length": 3.0,
    "outbound_line_distance_from_center": 4.0 + 1 / 12.0,
    "outbound_line_length": 4.0,
    # Outer paint
    "outer_paint_dims": [18.0 + 5 / 6, 16 - 1 / 3],
    # Inner paint
    "inner_paint_dims": [18.0 + 5 / 6, 12 - 1 / 3],
    # Center circle
    "outer_circle_radius": 6.0,
    "inner_circle_radius": 2.0,
    # Three point area
    "three_point_arc_angle": 68.13,
    "three_point_arc_diameter": 47.5,
    "three_point_line_length": 14.0,
    "three_point_side_width": 3.0,
    # Hoop height
    "hoop_height": 10.0,
}

wnba_court_parameters = {
    "court_dims": [94.0, 50.0],
    # Hoop area
    "hoop_distance_from_edge": 5.25,
    "hoop_radius": 0.75,
    # backboard properties
    "backboard_distance_from_edge": 4.0,
    "backboard_width": 6.0,
    "backboard_height": 3.5,
    "backboard_inner_rect_width": 2.0,
    "backboard_inner_rect_height": 1.5,
    "backboard_inner_rect_from_bottom": 1.0,
    # court properties
    "charge_circle_radius": 4.0,
    "charge_circle_side_length": 3.0,
    # Inbound lines
    "inbound_line_distance_from_edge": 28.0,
    "inbound_line_length": 3.0,
    "outbound_line_distance_from_center": 4.0 + 1 / 12.0,
    "outbound_line_length": 4.0,
    # Outer paint
    "outer_paint_dims": [18.0 + 5 / 6, 16 - 1 / 3],
    # Inner paint
    "inner_paint_dims": [18.0 + 5 / 6, 12 - 1 / 3],
    # Center circle
    "outer_circle_radius": 6.0,
    "inner_circle_radius": 2.0,
    # Three point area
    "three_point_arc_angle": 83.51692630710276,
    "three_point_arc_diameter": 44.365,
    "three_point_line_length": 7.75,
    "three_point_side_width": 3.0,
    # Hoop height
    "hoop_height": 10.0,
}

ncaa_court_parameters = {
    "court_dims": [94.0, 50.0],
    # Hoop area
    "hoop_distance_from_edge": 5.25,
    "hoop_radius": 0.75,
    # backboard properties
    "backboard_distance_from_edge": 4.0,
    "backboard_width": 6.0,
    "backboard_height": 3.5,
    "backboard_inner_rect_width": 2.0,
    "backboard_inner_rect_height": 1.5,
    "backboard_inner_rect_from_bottom": 1.0,
    # court properties
    "charge_circle_radius": 4.0,
    "charge_circle_side_length": 3.0,
    # Inbound lines
    "inbound_line_distance_from_edge": 28.0,
    "inbound_line_length": 3.0,
    "outbound_line_distance_from_center": 4.0 + 1 / 12.0,
    "outbound_line_length": 4.0,
    # Outer paint
    "outer_paint_dims": [18.0 + 5 / 6, 12 - 1 / 3],
    # Inner paint
    "inner_paint_dims": [18.0 + 5 / 6, 12 - 1 / 3],
    # Center circle
    "outer_circle_radius": 6.0,
    "inner_circle_radius": 6.0,
    # Three point area
    "three_point_arc_angle": 78.95,
    "three_point_arc_diameter": 44.218,
    "three_point_line_length": 9.4,
    "three_point_side_width": 3.34375,
    # Hoop height
    "hoop_height": 10.0,
}


fiba_court_parameters = {
    "court_dims": [91.8635, 49.2126],
    # Hoop area
    "hoop_distance_from_edge": 5.167,
    "hoop_radius": 0.75,
    # backboard properties
    "backboard_distance_from_edge": 3.937,
    "backboard_width": 6.0,
    "backboard_height": 3.5,
    "backboard_inner_rect_width": 2.0,
    "backboard_inner_rect_height": 1.5,
    "backboard_inner_rect_from_bottom": 1.0,
    # court properties
    "charge_circle_radius": 3.94,
    "charge_circle_side_length": 3.0,
    # Inbound lines
    "inbound_line_distance_from_edge": 27.32,
    "inbound_line_length": 3.0,
    "outbound_line_distance_from_center": 3.9685 + 1 / 12.0,
    "outbound_line_length": 4.0,
    # Outer paint
    "outer_paint_dims": [18.0289 + 5 / 6, 16.08 - 1 / 3],
    # Inner paint
    "inner_paint_dims": [18.0289 + 5 / 6, 12 - 1 / 3],
    # Center circle
    "outer_circle_radius": 5.90551,
    "inner_circle_radius": 5.90551,
    # Three point area
    "three_point_arc_angle": 78.9,
    "three_point_arc_diameter": 44.218,
    "three_point_line_length": 9.4,
    "three_point_side_width": 2.953,
    # Hoop height
    "hoop_height": 10.0,
}


def _get_court_params_in_desired_units(
    court_type: Literal["nba", "wnba", "ncaa", "fiba"],
    desired_units: Literal["m", "ft"],
):
    """
    Function to convert court parameters to units of choice.
    """
    assert court_type in ["nba", "wnba", "ncaa", "fiba"], "Invalid court type"
    assert desired_units in [
        "m",
        "ft",
    ], "Invalid units, Currently only 'm' and 'ft' are supported"

    if desired_units == "m":
        conversion_factor = 0.3048
    else:
        conversion_factor = 1.0

    if court_type == "nba":
        court_params = nba_court_parameters
    elif court_type == "wnba":
        court_params = wnba_court_parameters
    elif court_type == "ncaa":
        court_params = ncaa_court_parameters
    elif court_type == "fiba":
        court_params = fiba_court_parameters

    new_court_params = {}

    for key, value in court_params.items():
        if "angle" not in key.split("_"):
            if isinstance(value, list):
                new_court_params[key] = [val * conversion_factor for val in value]
            else:
                new_court_params[key] = value * conversion_factor
        else:
            new_court_params[key] = value

    return new_court_params


class LineDataUnits(lines.Line2D):
    def __init__(self, *args, **kwargs):
        _lw_data = kwargs.pop("linewidth", 1)
        super().__init__(*args, **kwargs)
        self._lw_data = _lw_data

    def _get_lw(self):
        if self.axes is not None:
            ppd = 72.0 / self.axes.figure.dpi
            trans = self.axes.transData.transform
            return ((trans((1, self._lw_data)) - trans((0, 0))) * ppd)[1]
        else:
            return self._lw_data

    def _set_lw(self, lw):
        self._lw_data = lw

    _linewidth = property(_get_lw, _set_lw)


class PatchDataUnits(patches.PathPatch):
    # https://stackoverflow.com/a/42972469/2912349
    def __init__(self, *args, **kwargs):
        _lw_data = kwargs.pop("linewidth", 1)
        super().__init__(*args, **kwargs)
        self._lw_data = _lw_data

    def _get_lw(self):
        if self.axes is not None:
            ppd = 72.0 / self.axes.figure.dpi
            trans = self.axes.transData.transform
            # the line mentioned below
            return ((trans((self._lw_data, self._lw_data)) - trans((0, 0))) * ppd)[1]
        else:
            return self._lw_data

    def _set_lw(self, lw):
        self._lw_data = lw

    _linewidth = property(_get_lw, _set_lw)


class Court:
    """
    A class to represent a basketball court and facilitate its plotting.

    Attributes:
    - court_type (str): Type of the court, either 'nba', 'wnba', 'ncaa' or 'fiba'.
    - units (str): Units of the court dimensions, either 'ft' or 'm'.
    - court_parameters (dict): Parameters defining the dimensions and characteristics of the court.
    - origin (np.array): The origin point of the court.

    Methods:
    - draw(ax, orientation, half, nrows, ncols, dpi, showaxis, court_color, paint_color, line_color, line_alpha, line_width, hoop_alpha, pad):
        Draws the basketball court according to specified parameters.

    Args:
    - court_type (str): Specifies the type of basketball court ('nba', 'wnba', 'ncaa' or 'fiba'). Defaults to 'nba'.

    Raises:
    - AssertionError: If the provided court_type is not 'nba', 'wnba', 'ncaa' or 'fiba'.
    """

    def __init__(
        self,
        court_type: Literal["nba", "wnba", "ncaa", "fiba"] = "nba",
        origin: Literal[
            "center", "top-left", "bottom-left", "top-right", "bottom-right"
        ] = "top-left",
        units: Literal["ft", "m"] = "ft",
    ):
        assert court_type in [
            "nba",
            "wnba",
            "ncaa",
            "fiba",
        ], "Invalid court_type. Please choose from ['nba', 'wnba', 'ncaa', 'fiba']"

        assert origin in [
            "center",
            "top-left",
            "bottom-left",
            "top-right",
            "bottom-right",
        ], "Invalid origin. Choose from 'center', '(top/bottom)-(left/right)'"

        assert units in [
            "m",
            "ft",
        ], "Invalid units. Currently only 'm' and 'ft' are supported"

        self.court_type = court_type
        self.units = units
        self.court_parameters = _get_court_params_in_desired_units(self.court_type, self.units)

        if origin == "center":
            self.origin = np.array([0.0, 0.0])
        elif origin == "top-left":
            self.origin = np.array(
                [
                    -self.court_parameters["court_dims"][0] / 2,
                    self.court_parameters["court_dims"][1] / 2,
                ]
            )
        elif origin == "bottom-left":
            self.origin = np.array(
                [
                    -self.court_parameters["court_dims"][0] / 2,
                    -self.court_parameters["court_dims"][1] / 2,
                ]
            )
        elif origin == "top-right":
            self.origin = np.array(
                [
                    self.court_parameters["court_dims"][0] / 2,
                    self.court_parameters["court_dims"][1] / 2,
                ]
            )
        elif origin == "bottom-right":
            self.origin = np.array(
                [
                    self.court_parameters["court_dims"][0] / 2,
                    -self.court_parameters["court_dims"][1] / 2,
                ]
            )

    def draw(
        self,
        ax: Axes | None = None,
        orientation: Literal["v", "h", "hl", "hr", "vu", "vd"] = "h",
        nrows=1,
        ncols=1,
        dpi=200,
        showaxis=False,
        court_color="none",
        paint_color="none",
        line_color="black",
        line_alpha=1.0,
        line_width=None,
        hoop_alpha=1.0,
        pad=5.0,
    ):
        """
        Draws the basketball court according to specified parameters.

        This method allows customization of the court's appearance and can plot either a full court or half-court in horizontal or vertical orientation.

        Args:
        - ax (matplotlib.axes.Axes, optional): The matplotlib axes to draw on. If None, a new figure and axes are created.
        - orientation (str): Orientation of the court. Defaults to 'h'.
        - nrows (int): Number of rows in the subplot grid. Defaults to 1.
        - ncols (int): Number of columns in the subplot grid. Defaults to 1.
        - dpi (int): Dots per inch for the plot. Defaults to 200.
        - showaxis (bool): Whether to show axis on the plot. Defaults to False.
        - court_color (str): Background color of the court. Defaults to 'none'.
        - paint_color (str): Color of the paint area. Defaults to 'none'.
        - line_color (str): Color of the lines on the court. Defaults to 'black'.
        - line_alpha (float): Transparency of court lines. Defaults to 1.
        - line_width (float): Width of the lines on the court in correct units. Defaults to None.
        - hoop_alpha (float): Transparency of the hoop. Defaults to 1.
        - pad (float): Padding around the court. Defaults to 5.

        Returns:
        - matplotlib.figure.Figure, matplotlib.axes.Axes: The figure and axes objects containing the court plot.

        Raises:
        - AssertionError: If orientation is not 'horizontal' or 'vertical', or if dpi is less than 200.
        """

        assert orientation in [
            "v",
            "h",
            "hl",
            "hr",
            "vu",
            "vd",
        ], "Invalid orientation. Choose 'horizontal' or 'vertical'"

        assert dpi >= 200, "DPI is too low"

        if len(orientation) > 1:
            half = orientation[1]
        else:
            half = None

        if line_width is None:
            if self.units == "ft":
                line_width = 1.0 / 6.0
            elif self.units == "m":
                line_width = 1.0 / 6.0 * 0.3045

        if ax is None:
            fig, axs = plt.subplots(nrows=nrows, ncols=ncols, dpi=dpi)
            if nrows == 1 and ncols == 1:
                if orientation[0] == "h":
                    self._draw_horizontal_court(
                        axs,
                        half,
                        court_color=court_color,
                        paint_color=paint_color,
                        line_color=line_color,
                        line_alpha=line_alpha,
                        line_width=line_width,
                        hoop_alpha=hoop_alpha,
                        pad=pad,
                    )
                elif orientation[0] == "v":
                    self._draw_vertical_court(
                        axs,
                        half,
                        court_color=court_color,
                        paint_color=paint_color,
                        line_color=line_color,
                        line_alpha=line_alpha,
                        line_width=line_width,
                        hoop_alpha=hoop_alpha,
                        pad=pad,
                    )
                if showaxis is False:
                    axs.axis("off")
                axs.set_aspect("equal")
                return fig, axs
            else:
                for ax in axs.flatten():
                    if orientation[0] == "h":
                        self._draw_horizontal_court(
                            ax,
                            half,
                            court_color=court_color,
                            paint_color=paint_color,
                            line_color=line_color,
                            line_alpha=line_alpha,
                            line_width=line_width,
                            hoop_alpha=hoop_alpha,
                            pad=pad,
                        )
                    elif orientation[0] == "v":
                        self._draw_vertical_court(
                            ax,
                            half,
                            court_color=court_color,
                            paint_color=paint_color,
                            line_color=line_color,
                            line_alpha=line_alpha,
                            line_width=line_width,
                            hoop_alpha=hoop_alpha,
                            pad=pad,
                        )
                    if showaxis is False:
                        ax.axis("off")
                    ax.set_aspect("equal")
            return fig, axs
        else:
            if orientation[0] == "h":
                self._draw_horizontal_court(
                    ax,
                    half,
                    court_color=court_color,
                    paint_color=paint_color,
                    line_color=line_color,
                    line_alpha=line_alpha,
                    line_width=line_width,
                    hoop_alpha=hoop_alpha,
                    pad=pad,
                )
            elif orientation[0] == "v":
                self._draw_vertical_court(
                    ax,
                    half,
                    court_color=court_color,
                    paint_color=paint_color,
                    line_color=line_color,
                    line_alpha=line_alpha,
                    line_width=line_width,
                    hoop_alpha=hoop_alpha,
                    pad=pad,
                )
            if showaxis is False:
                ax.axis("off")
            ax.set_aspect("equal")
            return ax

    def _draw_horizontal_court(
        self,
        ax: Axes,
        half,
        court_color,
        paint_color,
        line_color,
        line_alpha,
        line_width,
        hoop_alpha,
        pad,
    ):
        origin_shift_x, origin_shift_y = -self.origin
        court_x, court_y = self.court_parameters["court_dims"]
        cf = line_width / 2

        angle_a = 9.7800457882  # Angle 1 for lower FT line
        angle_b = 12.3415314172  # Angle 2 for lower FT line

        if half is None:
            ax.set_xlim(origin_shift_x - court_x / 2 - pad, origin_shift_x + court_x / 2 + pad)
            ax.set_ylim(origin_shift_y - court_y / 2 - pad, origin_shift_y + court_y / 2 + pad)
        elif half == "l":
            ax.set_xlim(origin_shift_x - court_x / 2 - pad, origin_shift_x + cf)
            ax.set_ylim(origin_shift_y - court_y / 2 - pad, origin_shift_y + court_y / 2 + pad)
        elif half == "r":
            ax.set_xlim(origin_shift_x - cf, origin_shift_x + court_x / 2 + pad)
            ax.set_ylim(origin_shift_y - court_y / 2 - pad, origin_shift_y + court_y / 2 + pad)

        # Draw the main court rectangle
        self._draw_rectangle(
            ax,
            origin_shift_x - court_x / 2 - cf,
            origin_shift_y - court_y / 2 - cf,
            court_x + 2 * cf,
            court_y + 2 * cf,
            line_width=line_width,
            line_color=line_color,
            line_style="-",
            face_color=court_color,
            alpha=line_alpha,
        )

        # Draw the outer paint areas
        outer_paint_x, outer_paint_y = self.court_parameters["outer_paint_dims"]
        # Left side
        if half is None or half == "l":
            self._draw_rectangle(
                ax,
                origin_shift_x - court_x / 2 - cf,
                origin_shift_y - outer_paint_y / 2 - cf,
                outer_paint_x + 2 * cf,
                outer_paint_y + 2 * cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                face_color=paint_color,
                alpha=line_alpha,
            )
        # Right side
        if half is None or half == "r":
            self._draw_rectangle(
                ax,
                origin_shift_x + court_x / 2 - outer_paint_x - cf,
                origin_shift_y - outer_paint_y / 2 - cf,
                outer_paint_x + 2 * cf,
                outer_paint_y + 2 * cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                face_color=paint_color,
                alpha=line_alpha,
            )

        inner_paint_x, inner_paint_y = self.court_parameters["inner_paint_dims"]

        # Draw the hoops
        left_hoop_x = (
            origin_shift_x - court_x / 2 + self.court_parameters["hoop_distance_from_edge"]
        )
        right_hoop_x = (
            origin_shift_x + court_x / 2 - self.court_parameters["hoop_distance_from_edge"]
        )
        # Left side
        if half is None or half == "l":
            self._draw_circle(
                ax,
                left_hoop_x,
                origin_shift_y,
                self.court_parameters["hoop_radius"],
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                face_color="none",
                alpha=hoop_alpha,
            )
        # Right side
        if half is None or half == "r":
            self._draw_circle(
                ax,
                right_hoop_x,
                origin_shift_y,
                self.court_parameters["hoop_radius"],
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                face_color="none",
                alpha=hoop_alpha,
            )
        # Draw the backboards
        bb_distance = self.court_parameters["backboard_distance_from_edge"]
        bb_width = self.court_parameters["backboard_width"]
        # Left side
        if half is None or half == "l":
            self._draw_line(
                ax,
                origin_shift_x - court_x / 2 + bb_distance,
                origin_shift_y - bb_width / 2,
                0.0,
                bb_width,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=hoop_alpha,
            )
        # Right side
        if half is None or half == "r":
            self._draw_line(
                ax,
                origin_shift_x + court_x / 2 - bb_distance,
                origin_shift_y - bb_width / 2,
                0.0,
                bb_width,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=hoop_alpha,
            )

        # Draw charge circles
        charge_diameter = 2 * self.court_parameters["charge_circle_radius"]
        # Left side
        if half is None or half == "l":
            self._draw_circular_arc(
                ax,
                left_hoop_x,
                origin_shift_y,
                charge_diameter + cf,
                angle=0,
                theta1=-90,
                theta2=90,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        # Right side
        if half is None or half == "r":
            self._draw_circular_arc(
                ax,
                right_hoop_x,
                origin_shift_y,
                charge_diameter + cf,
                angle=0,
                theta1=90,
                theta2=-90,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        # Draw the free throw arcs
        # Left-upper
        if half is None or half == "l":
            self._draw_circular_arc(
                ax,
                origin_shift_x - court_x / 2 + inner_paint_x + cf,
                origin_shift_y,
                inner_paint_y + 2 * cf,
                angle=0,
                theta1=-90,
                theta2=90,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            # # Left-lower
            if self.court_type in ["nba", "wnba"]:
                # Draw the first arc of angle 'a'
                self._draw_circular_arc(
                    ax,
                    origin_shift_x - court_x / 2 + inner_paint_x + cf,
                    origin_shift_y,
                    inner_paint_y + 2 * cf,
                    angle=0,
                    theta1=90,
                    theta2=90 + angle_a,
                    line_width=line_width,
                    line_color=line_color,
                    line_style="-",
                    alpha=line_alpha,
                )

                # Draw 13 arcs of angle 'b'
                for i in range(12):
                    start_angle = 90 + angle_a + i * angle_b
                    end_angle = start_angle + angle_b
                    color = line_color if i % 2 == 1 else paint_color

                    self._draw_circular_arc(
                        ax,
                        origin_shift_x - court_x / 2 + inner_paint_x + cf,
                        origin_shift_y,
                        inner_paint_y + 2 * cf,
                        angle=0,
                        theta1=start_angle,
                        theta2=end_angle,
                        line_width=line_width,
                        line_color=color,
                        line_style="-",
                        alpha=line_alpha,
                    )

                # Draw the final arc of angle 'a'
                self._draw_circular_arc(
                    ax,
                    origin_shift_x - court_x / 2 + inner_paint_x + cf,
                    origin_shift_y,
                    inner_paint_y + 2 * cf,
                    angle=0,
                    theta1=90 + angle_a + 13 * angle_b,
                    theta2=-90,
                    line_width=line_width,
                    line_color=line_color,
                    line_style="-",
                    alpha=line_alpha,
                )

        # Right side
        if half is None or half == "r":
            # Right-lower
            if self.court_type in ["nba", "wnba"]:
                # Draw the first arc of angle 'a'
                self._draw_circular_arc(
                    ax,
                    origin_shift_x + court_x / 2 - inner_paint_x - cf,
                    origin_shift_y,
                    inner_paint_y + 2 * cf,
                    angle=180,
                    theta1=90,
                    theta2=90 + angle_a,
                    line_width=line_width,
                    line_color=line_color,
                    line_style="-",
                    alpha=line_alpha,
                )

                # Draw 13 arcs of angle 'b'
                for i in range(12):
                    start_angle = 90 + angle_a + i * angle_b
                    end_angle = start_angle + angle_b
                    color = line_color if i % 2 == 1 else paint_color

                    self._draw_circular_arc(
                        ax,
                        origin_shift_x + court_x / 2 - inner_paint_x - cf,
                        origin_shift_y,
                        inner_paint_y + 2 * cf,
                        angle=180,
                        theta1=start_angle,
                        theta2=end_angle,
                        line_width=line_width,
                        line_color=color,
                        line_style="-",
                        alpha=line_alpha,
                    )

                # Draw the final arc of angle 'a'
                self._draw_circular_arc(
                    ax,
                    origin_shift_x + court_x / 2 - inner_paint_x - cf,
                    origin_shift_y,
                    inner_paint_y + 2 * cf,
                    angle=180,
                    theta1=90 + angle_a + 13 * angle_b,
                    theta2=-90,
                    line_width=line_width,
                    line_color=line_color,
                    line_style="-",
                    alpha=line_alpha,
                )

            # Right-upper
            self._draw_circular_arc(
                ax,
                origin_shift_x + court_x / 2 - inner_paint_x - cf,
                origin_shift_y,
                inner_paint_y + 2 * cf,
                angle=0,
                theta1=90,
                theta2=-90,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        # Draw inbound lines
        ib_line_distance = self.court_parameters["inbound_line_distance_from_edge"]
        ib_line_length = self.court_parameters["inbound_line_length"]
        ob_line_distance = self.court_parameters["outbound_line_distance_from_center"]
        ob_line_length = self.court_parameters["outbound_line_length"]
        # Left side
        if half is None or half == "l":
            self._draw_line(
                ax,
                origin_shift_x - court_x / 2 + ib_line_distance + cf,
                origin_shift_y + court_y / 2,
                0.0,
                -ib_line_length + cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            self._draw_line(
                ax,
                origin_shift_x - court_x / 2 + ib_line_distance + cf,
                origin_shift_y - court_y / 2,
                0.0,
                ib_line_length - cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            self._draw_line(
                ax,
                origin_shift_x - ob_line_distance,
                origin_shift_y + court_y / 2 + cf,
                0.0,
                ob_line_length - cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        # Right side
        if half is None or half == "r":
            self._draw_line(
                ax,
                origin_shift_x + court_x / 2 - ib_line_distance + cf,
                origin_shift_y + court_y / 2,
                0.0,
                -ib_line_length + cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            self._draw_line(
                ax,
                origin_shift_x + court_x / 2 - ib_line_distance + cf,
                origin_shift_y - court_y / 2,
                0.0,
                ib_line_length - cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            self._draw_line(
                ax,
                origin_shift_x + ob_line_distance,
                origin_shift_y + court_y / 2 + cf,
                0.0,
                ob_line_length - cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        # Draw three point areas
        # Draw the arcs arcs
        arc_diameter = self.court_parameters["three_point_arc_diameter"] - line_width / 2
        arc_angle = self.court_parameters["three_point_arc_angle"]
        # Left arc
        if half is None or half == "l":
            self._draw_circular_arc(
                ax,
                left_hoop_x,
                origin_shift_y,
                arc_diameter - 2 * cf,
                angle=0,
                theta1=-arc_angle,
                theta2=arc_angle,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        # Right arc
        if half is None or half == "r":
            self._draw_circular_arc(
                ax,
                right_hoop_x,
                origin_shift_y,
                arc_diameter - 2 * cf,
                angle=180.0,
                theta1=-arc_angle,
                theta2=arc_angle,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        # Draw the side lines
        line_length_3pt = self.court_parameters["three_point_line_length"]
        side_width_3pt = self.court_parameters["three_point_side_width"]
        # Left-upper side
        if half is None or half == "l":
            self._draw_line(
                ax,
                origin_shift_x - court_x / 2,
                origin_shift_y + court_y / 2 - side_width_3pt - cf,
                line_length_3pt,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            # Left-lower side
            self._draw_line(
                ax,
                origin_shift_x - court_x / 2,
                origin_shift_y - court_y / 2 + side_width_3pt + cf,
                line_length_3pt,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        if half is None or half == "r":
            # Right-upper side
            self._draw_line(
                ax,
                origin_shift_x + court_x / 2 - line_length_3pt,
                origin_shift_y + court_y / 2 - side_width_3pt - cf,
                line_length_3pt,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            # Right-lower side
            self._draw_line(
                ax,
                origin_shift_x + court_x / 2 - line_length_3pt,
                origin_shift_y - court_y / 2 + side_width_3pt + cf,
                line_length_3pt,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        # Draw center line
        self._draw_line(
            ax,
            origin_shift_x,
            origin_shift_y - court_y / 2,
            0.0,
            court_y,
            line_width=line_width,
            line_color=line_color,
            line_style="-",
            alpha=line_alpha,
        )

        # Draw the center circles
        # Outer circle
        self._draw_circle(
            ax,
            origin_shift_x,
            origin_shift_y,
            self.court_parameters["outer_circle_radius"],
            line_width=line_width,
            line_color=line_color,
            line_style="-",
            face_color=paint_color,
            alpha=line_alpha,
        )
        # Inner circle
        self._draw_circle(
            ax,
            origin_shift_x,
            origin_shift_y,
            self.court_parameters["inner_circle_radius"],
            line_width=line_width,
            line_color=line_color,
            line_style="-",
            face_color=paint_color,
            alpha=line_alpha,
        )

    def _draw_vertical_court(
        self,
        ax: Axes,
        half,
        court_color,
        paint_color,
        line_color,
        line_alpha,
        line_width,
        hoop_alpha,
        pad,
    ):
        court_x, court_y = self.court_parameters["court_dims"]
        origin_shift_x, origin_shift_y = -self.origin

        angle_a = 9.7800457882  # Angle 1 for lower FT line
        angle_b = 12.3415314172  # Angle 2 for lower FT line

        cf = line_width / 2

        if half is None:
            ax.set_ylim(origin_shift_x - court_x / 2 - pad, origin_shift_x + court_x / 2 + pad)
            ax.set_xlim(-origin_shift_y - court_y / 2 - pad, -origin_shift_y + court_y / 2 + pad)
        elif half == "d":
            ax.set_ylim(origin_shift_x - court_x / 2 - pad, origin_shift_x + cf)
            ax.set_xlim(-origin_shift_y - court_y / 2 - pad, -origin_shift_y + court_y / 2 + pad)
        elif half == "u":
            ax.set_ylim(origin_shift_x - cf, origin_shift_x + court_x / 2 + pad)
            ax.set_xlim(-origin_shift_y - court_y / 2 - pad, -origin_shift_y + court_y / 2 + pad)

        # Draw the main court rectangle
        self._draw_rectangle(
            ax,
            -origin_shift_y - court_y / 2 - cf,
            origin_shift_x - court_x / 2 - cf,
            court_y + 2 * cf,
            court_x + 2 * cf,
            line_width=line_width,
            line_color=line_color,
            line_style="-",
            face_color=court_color,
            alpha=line_alpha,
        )

        # Draw the outer paint areas
        outer_paint_x, outer_paint_y = self.court_parameters["outer_paint_dims"]
        # Left side
        if half is None or half == "d":
            self._draw_rectangle(
                ax,
                -origin_shift_y - outer_paint_y / 2 - cf,
                origin_shift_x - court_x / 2 - cf,
                outer_paint_y + 2 * cf,
                outer_paint_x + 2 * cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                face_color=paint_color,
                alpha=line_alpha,
            )
        # Right side
        if half is None or half == "u":
            self._draw_rectangle(
                ax,
                -origin_shift_y - outer_paint_y / 2 - cf,
                origin_shift_x + court_x / 2 - outer_paint_x - cf,
                outer_paint_y + 2 * cf,
                outer_paint_x + 2 * cf,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                face_color=paint_color,
                alpha=line_alpha,
            )

        inner_paint_x, inner_paint_y = self.court_parameters["inner_paint_dims"]

        # Draw the hoops
        left_hoop_x = (
            origin_shift_x - court_x / 2 + self.court_parameters["hoop_distance_from_edge"]
        )
        right_hoop_x = (
            origin_shift_x + court_x / 2 - self.court_parameters["hoop_distance_from_edge"]
        )
        # Left side
        if half is None or half == "d":
            self._draw_circle(
                ax,
                -origin_shift_y,
                left_hoop_x,
                self.court_parameters["hoop_radius"],
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                face_color="none",
                alpha=hoop_alpha,
            )
        # Right side
        if half is None or half == "u":
            self._draw_circle(
                ax,
                -origin_shift_y,
                right_hoop_x,
                self.court_parameters["hoop_radius"],
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                face_color="none",
                alpha=hoop_alpha,
            )

        # Draw the backboards
        bb_distance = self.court_parameters["backboard_distance_from_edge"]
        bb_width = self.court_parameters["backboard_width"]
        # Left side
        if half is None or half == "d":
            self._draw_line(
                ax,
                -origin_shift_y - bb_width / 2,
                origin_shift_x - court_x / 2 + bb_distance,
                bb_width,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=hoop_alpha,
            )
        # Right side
        if half is None or half == "u":
            self._draw_line(
                ax,
                -origin_shift_y - bb_width / 2,
                origin_shift_x + court_x / 2 - bb_distance,
                bb_width,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=hoop_alpha,
            )

        # Draw charge circles
        charge_diameter = 2 * self.court_parameters["charge_circle_radius"]
        # Left side
        if half is None or half == "d":
            self._draw_circular_arc(
                ax,
                -origin_shift_y,
                left_hoop_x,
                charge_diameter + cf,
                angle=0,
                theta1=0,
                theta2=180,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        # Right side
        if half is None or half == "u":
            self._draw_circular_arc(
                ax,
                -origin_shift_y,
                right_hoop_x,
                charge_diameter + cf,
                angle=0,
                theta1=180,
                theta2=0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        # Draw the free throw arcs
        # Left-upper
        if half is None or half == "d":
            self._draw_circular_arc(
                ax,
                -origin_shift_y,
                origin_shift_x - court_x / 2 + inner_paint_x + cf,
                inner_paint_y + 2 * cf,
                angle=0,
                theta1=0,
                theta2=180,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            # # Left-lower
            if self.court_type in ["nba", "wnba"]:
                # Draw the first arc of angle 'a'
                self._draw_circular_arc(
                    ax,
                    -origin_shift_y,
                    origin_shift_x - court_x / 2 + inner_paint_x + cf,
                    inner_paint_y + 2 * cf,
                    angle=90,
                    theta1=90,
                    theta2=90 + angle_a,
                    line_width=line_width,
                    line_color=line_color,
                    line_style="-",
                    alpha=line_alpha,
                )

                # Draw 13 arcs of angle 'b'
                for i in range(12):
                    start_angle = 90 + angle_a + i * angle_b
                    end_angle = start_angle + angle_b
                    color = line_color if i % 2 == 1 else paint_color

                    self._draw_circular_arc(
                        ax,
                        -origin_shift_y,
                        origin_shift_x - court_x / 2 + inner_paint_x + cf,
                        inner_paint_y + 2 * cf,
                        angle=90,
                        theta1=start_angle,
                        theta2=end_angle,
                        line_width=line_width,
                        line_color=color,
                        line_style="-",
                        alpha=line_alpha,
                    )

                # Draw the final arc of angle 'a'
                self._draw_circular_arc(
                    ax,
                    -origin_shift_y,
                    origin_shift_x - court_x / 2 + inner_paint_x + cf,
                    inner_paint_y + 2 * cf,
                    angle=90,
                    theta1=90 + angle_a + 13 * angle_b,
                    theta2=-90,
                    line_width=line_width,
                    line_color=line_color,
                    line_style="-",
                    alpha=line_alpha,
                )

        # Right side
        if half is None or half == "u":
            # Right-lower
            if self.court_type in ["nba", "wnba"]:
                # Draw the first arc of angle 'a'
                self._draw_circular_arc(
                    ax,
                    -origin_shift_y,
                    origin_shift_x + court_x / 2 - inner_paint_x - cf,
                    inner_paint_y + 2 * cf,
                    angle=270,
                    theta1=90,
                    theta2=90 + angle_a,
                    line_width=line_width,
                    line_color=line_color,
                    line_style="-",
                    alpha=line_alpha,
                )

                # Draw 13 arcs of angle 'b'
                for i in range(12):
                    start_angle = 90 + angle_a + i * angle_b
                    end_angle = start_angle + angle_b
                    color = line_color if i % 2 == 1 else paint_color

                    self._draw_circular_arc(
                        ax,
                        -origin_shift_y,
                        origin_shift_x + court_x / 2 - inner_paint_x - cf,
                        inner_paint_y + 2 * cf,
                        angle=270,
                        theta1=start_angle,
                        theta2=end_angle,
                        line_width=line_width,
                        line_color=color,
                        line_style="-",
                        alpha=line_alpha,
                    )

                # Draw the final arc of angle 'a'
                self._draw_circular_arc(
                    ax,
                    -origin_shift_y,
                    origin_shift_x + court_x / 2 - inner_paint_x - cf,
                    inner_paint_y + 2 * cf,
                    angle=270,
                    theta1=90 + angle_a + 13 * angle_b,
                    theta2=-90,
                    line_width=line_width,
                    line_color=line_color,
                    line_style="-",
                    alpha=line_alpha,
                )

            # Right-upper
            self._draw_circular_arc(
                ax,
                -origin_shift_y,
                origin_shift_x + court_x / 2 - inner_paint_x - cf,
                inner_paint_y + 2 * cf,
                angle=0,
                theta1=180,
                theta2=0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        # Draw inbound lines
        ib_line_distance = self.court_parameters["inbound_line_distance_from_edge"]
        ib_line_length = self.court_parameters["inbound_line_length"]
        ob_line_distance = self.court_parameters["outbound_line_distance_from_center"]
        ob_line_length = self.court_parameters["outbound_line_length"]
        # Left side
        if half is None or half == "d":
            self._draw_line(
                ax,
                -origin_shift_y + court_y / 2,
                origin_shift_x - court_x / 2 + ib_line_distance + cf,
                -ib_line_length + cf,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            self._draw_line(
                ax,
                -origin_shift_y - court_y / 2,
                origin_shift_x - court_x / 2 + ib_line_distance + cf,
                ib_line_length - cf,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            self._draw_line(
                ax,
                -origin_shift_y - court_y / 2 - cf,
                origin_shift_x - ob_line_distance,
                -ob_line_length + cf,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        # Right side
        if half is None or half == "u":
            self._draw_line(
                ax,
                -origin_shift_y + court_y / 2,
                origin_shift_x + court_x / 2 - ib_line_distance + cf,
                -ib_line_length + cf,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            self._draw_line(
                ax,
                -origin_shift_y - court_y / 2,
                origin_shift_x + court_x / 2 - ib_line_distance + cf,
                ib_line_length - cf,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            self._draw_line(
                ax,
                -origin_shift_y - court_y / 2 - cf,
                origin_shift_x + ob_line_distance,
                -ob_line_length + cf,
                0.0,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        # Draw three point areas
        # Draw the arcs arcs
        arc_diameter = self.court_parameters["three_point_arc_diameter"] - line_width / 2
        arc_angle = self.court_parameters["three_point_arc_angle"]
        # Left arc
        if half is None or half == "d":
            self._draw_circular_arc(
                ax,
                -origin_shift_y,
                left_hoop_x,
                arc_diameter - 2 * cf,
                angle=0,
                theta1=90 - arc_angle,
                theta2=90 + arc_angle,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        # Right arc
        if half is None or half == "u":
            self._draw_circular_arc(
                ax,
                -origin_shift_y,
                right_hoop_x,
                arc_diameter - 2 * cf,
                angle=180.0,
                theta1=90 - arc_angle,
                theta2=arc_angle + 90,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
        # Draw the side lines
        line_length_3pt = self.court_parameters["three_point_line_length"]
        side_width_3pt = self.court_parameters["three_point_side_width"]
        if half is None or half == "d":
            # Left-upper side
            self._draw_line(
                ax,
                -origin_shift_y + court_y / 2 - side_width_3pt - cf,
                origin_shift_x - court_x / 2,
                0.0,
                line_length_3pt,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

            # Left-lower side
            self._draw_line(
                ax,
                -origin_shift_y - court_y / 2 + side_width_3pt + cf,
                origin_shift_x - court_x / 2,
                0.0,
                line_length_3pt,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        if half is None or half == "u":
            # Right-upper side
            self._draw_line(
                ax,
                -origin_shift_y + court_y / 2 - side_width_3pt - cf,
                origin_shift_x + court_x / 2 - line_length_3pt,
                0.0,
                line_length_3pt,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )
            # Right-lower side
            self._draw_line(
                ax,
                -origin_shift_y - court_y / 2 + side_width_3pt + cf,
                origin_shift_x + court_x / 2 - line_length_3pt,
                0.0,
                line_length_3pt,
                line_width=line_width,
                line_color=line_color,
                line_style="-",
                alpha=line_alpha,
            )

        # Draw center line
        self._draw_line(
            ax,
            -origin_shift_y - court_y / 2,
            origin_shift_x,
            court_y,
            0.0,
            line_width=line_width,
            line_color=line_color,
            line_style="-",
            alpha=line_alpha,
        )

        # Draw the center circles

        # Outer circle
        self._draw_circle(
            ax,
            -origin_shift_y,
            origin_shift_x,
            self.court_parameters["outer_circle_radius"],
            line_width=line_width,
            line_color=line_color,
            line_style="-",
            face_color=paint_color,
            alpha=line_alpha,
        )

        # Inner circle
        self._draw_circle(
            ax,
            -origin_shift_y,
            origin_shift_x,
            self.court_parameters["inner_circle_radius"],
            line_width=line_width,
            line_color=line_color,
            line_style="-",
            face_color=paint_color,
            alpha=line_alpha,
        )

    def _draw_rectangle(
        self,
        ax: Axes,
        x0: float | int,
        y0: float | int,
        len_x: float | int,
        len_y: float | int,
        line_width,
        line_color,
        line_style,
        face_color,
        alpha,
    ):
        rectangle = patches.Rectangle(
            (x0, y0),
            len_x,
            len_y,
            linewidth=line_width,
            edgecolor=line_color,
            linestyle=line_style,
            facecolor=face_color,
            alpha=alpha,
        )
        path = rectangle.get_path().transformed(rectangle.get_patch_transform())
        pathpatch = PatchDataUnits(
            path,
            facecolor=face_color,
            edgecolor=line_color,
            linewidth=line_width,
            linestyle=line_style,
        )
        ax.add_patch(pathpatch)

    def _draw_line(
        self,
        ax: Axes,
        x0: float | int,
        y0: float | int,
        dx: float | int,
        dy: float | int,
        line_width,
        line_color,
        line_style,
        alpha,
    ):
        line = LineDataUnits(
            [x0, x0 + dx],
            [y0, y0 + dy],
            linewidth=line_width,
            color=line_color,
            linestyle=line_style,
            alpha=alpha,
        )
        ax.add_line(line)

    def _draw_circle(
        self,
        ax: Axes,
        x0: float | int,
        y0: float | int,
        diameter,
        line_width,
        line_color,
        line_style,
        face_color,
        alpha,
    ):
        circle = patches.Circle(
            (x0, y0),
            diameter,
            linewidth=line_width,
            edgecolor=line_color,
            linestyle=line_style,
            facecolor=face_color,
            alpha=alpha,
        )
        path = circle.get_path().transformed(circle.get_patch_transform())
        pathpatch = PatchDataUnits(
            path,
            facecolor=face_color,
            edgecolor=line_color,
            linewidth=line_width,
            linestyle=line_style,
        )
        ax.add_patch(pathpatch)

    def _draw_circular_arc(
        self,
        ax: Axes,
        x0: float | int,
        y0: float | int,
        diameter,
        angle: float,
        theta1: float,
        theta2: float,
        line_width,
        line_color,
        line_style,
        alpha,
    ):
        circular_arc = patches.Arc(
            (x0, y0),
            diameter,
            diameter,
            angle=angle,
            theta1=theta1,
            theta2=theta2,
            linewidth=line_width,
            edgecolor=line_color,
            ls=line_style,
            alpha=alpha,
        )
        path = circular_arc.get_path().transformed(circular_arc.get_patch_transform())
        pathpatch = PatchDataUnits(
            path,
            facecolor="none",
            edgecolor=line_color,
            linewidth=line_width,
            linestyle=line_style,
        )
        ax.add_patch(pathpatch)


# ---------- styling helpers (basketball traces + draw_trajectories_on_court) ----------
COLOR_BALL = (0.85, 0.20, 0.18)  # red-ish
COLOR_HOME = (0.15, 0.40, 0.85)  # blue-ish
COLOR_AWAY = (0.10, 0.75, 0.35)  # green-ish


def _fade_line(ax, xy, color, lw=2.2, alpha_min=0.15, alpha_max=1.0, z=3):
    """
    Draw polyline with segment-wise fading (start=alpha_min -> end=alpha_max).
    xy: (T,2)
    """
    xy = np.asarray(xy, dtype=float)
    if len(xy) < 2:
        return
    segs = np.concatenate([xy[:-1, None, :], xy[1:, None, :]], axis=1)  # (T-1, 2, 2)
    n = segs.shape[0]
    alphas = np.linspace(alpha_min, alpha_max, n)
    rgba = np.tile((*color, 1.0), (n, 1))
    rgba[:, 3] = alphas
    lc = LineCollection(segs, colors=rgba, linewidths=lw, zorder=z, capstyle="round")
    ax.add_collection(lc)


def render_basketball_observed_gt_panel(
    trajectory: np.ndarray,
    obs_mask: np.ndarray,
    *,
    trace_lw: float = 3.5,
) -> np.ndarray:
    """
    Single static court image: per agent, faded GT polyline from t=0 through the last
    observed timestep (``obs_mask[t, a] >= 0.5``). Agents with no observed steps are
    skipped.

    ``trajectory`` is ``(T, N, 2)`` in court units (feet). ``obs_mask`` is ``(T, N)``.
    """
    traj = np.asarray(trajectory, dtype=float)
    mask = np.asarray(obs_mask, dtype=float)
    if traj.ndim != 3 or traj.shape[-1] != 2:
        raise ValueError(f"Expected trajectory (T, N, 2), got shape {traj.shape}")
    if mask.shape != traj.shape[:2]:
        raise ValueError(
            f"obs_mask shape {mask.shape} does not match trajectory " f"(T, N) {traj.shape[:2]}"
        )
    t_len, n_ent, _ = traj.shape

    fig, ax = plt.subplots(1, 1, figsize=(7.5, 4), dpi=32)
    court = Court(court_type="nba", origin="bottom-left", units="ft")
    court.draw(ax=ax, showaxis=False, pad=COURT_PAD_FT)

    def _draw_entity(entity_idx: int, color: tuple, z: int) -> None:
        if entity_idx < 0 or entity_idx >= n_ent:
            return
        observed = mask[:, entity_idx] >= 0.5
        if not np.any(observed):
            return
        t_end = int(np.flatnonzero(observed)[-1])
        up_to = t_end + 1
        xy = traj[0:up_to, entity_idx, :]
        if xy.shape[0] >= 2:
            _fade_line(
                ax,
                xy,
                color,
                lw=trace_lw,
                alpha_min=0.22,
                alpha_max=1.0,
                z=z,
            )
        else:
            ax.scatter(
                [xy[0, 0]],
                [xy[0, 1]],
                s=36,
                c=[color],
                edgecolors="white",
                linewidths=0.9,
                zorder=z + 1,
            )

    for i in range(min(5, n_ent)):
        _draw_entity(i, COLOR_HOME, z=3)
    for i in range(5, min(10, n_ent)):
        _draw_entity(i, COLOR_AWAY, z=3)
    for i in range(10, n_ent):
        _draw_entity(i, COLOR_BALL, z=5)

    fig.canvas.draw()
    if hasattr(fig.canvas, "buffer_rgba"):
        rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    elif hasattr(fig.canvas, "tostring_argb"):
        argb = np.asarray(fig.canvas.tostring_argb(), dtype=np.uint8)
        rgba = argb[..., [1, 2, 3, 0]]
    else:
        raise RuntimeError("Matplotlib canvas has no buffer_rgba or tostring_argb")
    rgb = rgba[..., :3]

    plt.close(fig)
    return rgb


def create_basketball_frame(
    trajectory: np.ndarray,
    frame_idx: int,
    *,
    history: int = 5,
    trace_lw: float = 3.5,
    ball_trace: bool = True,
) -> np.ndarray:
    """
    Render one basketball court frame with a short motion trace per entity.

    ``trajectory`` has shape ``(T, N, 2)`` in court units. For frame ``frame_idx``,
    draws up to ``history`` positions ending at the current time (weak alpha for
    older segments, strong for the newest), then home, away, ball (indices
    ``0:5``, ``5:10``, ``10:``) so the ball appears on top.

    If ``ball_trace`` is False, players keep traces but the ball is drawn only at
    its current position (no motion history for the ball).
    """
    traj = np.asarray(trajectory, dtype=float)
    if traj.ndim != 3 or traj.shape[-1] != 2:
        raise ValueError(f"Expected trajectory (T, N, 2), got shape {traj.shape}")
    t_len, n_ent, _ = traj.shape
    if frame_idx < 0 or frame_idx >= t_len:
        raise ValueError(f"frame_idx {frame_idx} out of range for T={t_len}")
    hist_n = max(1, int(history))

    fig, ax = plt.subplots(1, 1, figsize=(7.5, 4), dpi=32)
    court = Court(court_type="nba", origin="bottom-left", units="ft")
    court.draw(ax=ax, showaxis=False, pad=COURT_PAD_FT)

    def _trace_entity(entity_idx: int, color: tuple, z: int) -> None:
        if entity_idx < 0 or entity_idx >= n_ent:
            return
        t0 = max(0, frame_idx - hist_n + 1)
        xy = traj[t0 : frame_idx + 1, entity_idx, :]
        if xy.shape[0] >= 2:
            _fade_line(
                ax,
                xy,
                color,
                lw=trace_lw,
                alpha_min=0.22,
                alpha_max=1.0,
                z=z,
            )
        else:
            ax.scatter(
                [xy[0, 0]],
                [xy[0, 1]],
                s=36,
                c=[color],
                edgecolors="white",
                linewidths=0.9,
                zorder=z + 1,
            )

    def _ball_current_only(entity_idx: int, color: tuple, z: int) -> None:
        if entity_idx < 0 or entity_idx >= n_ent:
            return
        xy = traj[frame_idx, entity_idx, :]
        ax.scatter(
            [xy[0]],
            [xy[1]],
            s=35,
            c=[color],
            edgecolors="white",
            linewidths=0.9,
            zorder=z + 1,
        )

    for i in range(min(5, n_ent)):
        _trace_entity(i, COLOR_HOME, z=3)
    for i in range(5, min(10, n_ent)):
        _trace_entity(i, COLOR_AWAY, z=3)
    for i in range(10, n_ent):
        if ball_trace:
            _trace_entity(i, COLOR_BALL, z=5)
        else:
            _ball_current_only(i, COLOR_BALL, z=5)

    fig.canvas.draw()  # ensure the renderer has drawn
    w, h = fig.canvas.get_width_height()
    # Prefer buffer_rgba if available
    if hasattr(fig.canvas, "buffer_rgba"):
        rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    # Fallback: MacOSX often only has ARGB
    elif hasattr(fig.canvas, "tostring_argb"):
        argb = np.asarray(fig.canvas.tostring_argb(), dtype=np.uint8)
        # Convert ARGB -> RGBA (move alpha from channel 0 to the end)
        rgba = argb[..., [1, 2, 3, 0]]
    rgb = rgba[..., :3]

    plt.close(fig)  # avoid memory leak

    return rgb


def create_soccer_frame(pts: np.ndarray) -> np.ndarray:
    """
    create a soccer frame
    """
    from mplsoccer import Pitch

    fig, ax = plt.subplots(1, 1, figsize=(10, 5.75), dpi=32)
    pitch = Pitch(pitch_color=None, line_color="grey", stripe=False)
    pitch.draw(ax=ax)
    pts = pts / np.array([[3840, 2160]]) * np.array([[105, 68]])
    for pt in pts[-1:]:
        pitch.scatter(pt[0], pt[1], color="red", ax=ax)
    for pt in pts[0:11]:
        pitch.scatter(pt[0], pt[1], color="blue", ax=ax)
    for pt in pts[11:22]:
        pitch.scatter(pt[0], pt[1], color="green", ax=ax)
    fig.canvas.draw()  # ensure the renderer has drawn
    w, h = fig.canvas.get_width_height()
    if hasattr(fig.canvas, "buffer_rgba"):
        rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    elif hasattr(fig.canvas, "tostring_argb"):
        argb = np.asarray(fig.canvas.tostring_argb(), dtype=np.uint8)
        rgba = argb[..., [1, 2, 3, 0]]
    rgb = rgba[..., :3]
    plt.close(fig)  # avoid memory leak
    return rgb


def create_football_frame(pts: np.ndarray) -> np.ndarray:
    """
    create a football frame
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 4.5), dpi=32)
    pts = pts / np.array([[120, 53.3]]) * np.array([[640, 288]])
    for pt in pts[-1:]:
        ax.scatter(pt[0], pt[1], color="red")
    for pt in pts[0:11]:
        ax.scatter(pt[0], pt[1], color="blue")
    for pt in pts[11:22]:
        ax.scatter(pt[0], pt[1], color="green")
    ax.set_xlim(0, 640)
    ax.set_ylim(0, 288)
    fig.canvas.draw()  # ensure the renderer has drawn
    w, h = fig.canvas.get_width_height()
    if hasattr(fig.canvas, "buffer_rgba"):
        rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    elif hasattr(fig.canvas, "tostring_argb"):
        argb = np.asarray(fig.canvas.tostring_argb(), dtype=np.uint8)
        rgba = argb[..., [1, 2, 3, 0]]
    rgb = rgba[..., :3]
    plt.close(fig)  # avoid memory leak
    return rgb


def create_frames_from_trajectory(
    trajectory: np.ndarray,
    game: str,
    *,
    basketball_ball_trace: bool = False,
) -> list[np.ndarray]:
    """
    create frames from a trajectory

    For basketball, ``basketball_ball_trace`` controls whether the ball (indices
    ``>= 10``) gets a short motion trace; when False, only the current ball
    position is drawn (players still get traces).
    """
    frames = []
    traj = np.asarray(trajectory)
    if game == "basketball":
        for t in range(traj.shape[0]):
            frames.append(create_basketball_frame(traj, t, ball_trace=basketball_ball_trace))
        return frames
    for pts in trajectory:
        if game == "soccer":
            frame = create_soccer_frame(pts)
        elif game == "football":
            frame = create_football_frame(pts)
        else:
            raise ValueError(f"Unknown game: {game}")
        frames.append(frame)
    return frames


def create_video_from_frames(frames: list[np.ndarray], video_path: str, fps: int = 10):
    """
    create a video from a list of frames
    """
    mimsave(video_path, frames, fps=fps)


def _end_marker(ax, xy, color, size=36, edge="white", edge_w=1.2, z=5):
    if len(xy) == 0:
        return
    ax.scatter(
        [xy[-1, 0]],
        [xy[-1, 1]],
        s=size,
        c=[color],
        edgecolor=edge,
        linewidths=edge_w,
        zorder=z,
    )


def _direction_arrow(
    ax,
    xy,
    color,
    lw=1.8,
    z=4,
    *,
    mutation_scale: float | None = None,
):
    if len(xy) < 2:
        return
    p, q = xy[-2], xy[-1]
    d = q - p
    if float(np.linalg.norm(d)) < 1e-9:
        return
    props: dict = dict(arrowstyle="->", color=color, lw=lw)
    if mutation_scale is not None:
        props["mutation_scale"] = mutation_scale
    ax.annotate(
        "",
        xy=q,
        xytext=p,
        arrowprops=props,
        zorder=z,
    )


# ---------- main drawing ----------
def draw_trajectories_on_court(
    ax,
    data: np.ndarray,
    obs_len=None,  # int | None  number of "past" steps to render lighter
    lw=2.2,
):
    """
    Uses the existing axes (already containing the court) and overlays trajectories.
    Coordinates must be in the SAME units/origin as your Court (typically feet).

    Example players dict:
    players = {
        "home_23": {"xy": np.array([[x0,y0], ... [xT,yT]]), "team": "home"},
        "away_7":  {"xy": np.array([...]),                   "team": "away"},
    }
    """

    def _draw_one(xy, color):
        xy = np.asarray(xy, dtype=float)
        if obs_len is None or obs_len <= 1 or obs_len >= len(xy):
            _fade_line(ax, xy, color, lw=lw, alpha_min=0.20, alpha_max=1.0)
        else:
            past, fut = xy[:obs_len], xy[obs_len:]
            _fade_line(ax, past, color, lw=lw * 0.95, alpha_min=0.10, alpha_max=0.60)
            _fade_line(ax, fut, color, lw=lw * 1.10, alpha_min=0.60, alpha_max=1.00)
        _end_marker(ax, xy, color)
        _direction_arrow(ax, xy, color, mutation_scale=16)

    # players
    for player_idx in range(10):
        player_data = data[:, player_idx, :]
        color = COLOR_HOME if player_idx < 5 else COLOR_AWAY
        _draw_one(player_data, color)

    ball_data = data[:, 10, :]
    _draw_one(ball_data, COLOR_BALL)


def render_scene(
    data: np.array,
    court_type="nba",
    origin="bottom-left",  # matches your example
    units="ft",
    orientation="h",  # "h", "v", "hl", "hr", "vu", "vd"
    obs_len=None,
    figsize=(7.5, 4),
    dpi=200,
    showaxis=False,
    save_path=None,
):
    fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
    court = Court(court_type=court_type, origin=origin, units=units)
    court.draw(
        ax=ax, orientation=orientation, showaxis=showaxis, pad=COURT_PAD_FT
    )
    draw_trajectories_on_court(ax, data, obs_len=obs_len)
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)  # avoid memory leak
    return fig, ax


def _static_view_fill_axes(fig, ax) -> None:
    """Remove default figure margins so the court uses the full bitmap (like court_image)."""
    fig.subplots_adjust(0, 0, 1, 1, wspace=0, hspace=0)
    ax.set_position([0, 0, 1, 1])


def render_scene_to_rgb(
    data: np.ndarray,
    court_type: str = "nba",
    origin: str = "bottom-left",
    units: str = "ft",
    orientation: str = "h",
    obs_len=None,
    figsize=(7.5, 4),
    dpi: int = STATIC_VIEW_DPI,
    showaxis: bool = False,
    *,
    court_pad_ft: float = STATIC_VIEW_PAD_FT,
) -> np.ndarray:
    """Render one frame as uint8 HxWx3 (court + trajectories), for video export."""
    fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
    _static_view_fill_axes(fig, ax)
    court = Court(court_type=court_type, origin=origin, units=units)
    court.draw(
        ax=ax, orientation=orientation, showaxis=showaxis, pad=court_pad_ft
    )
    draw_trajectories_on_court(ax, data, obs_len=obs_len)
    fig.canvas.draw()
    if hasattr(fig.canvas, "buffer_rgba"):
        rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    elif hasattr(fig.canvas, "tostring_argb"):
        argb = np.asarray(fig.canvas.tostring_argb(), dtype=np.uint8)
        rgba = argb[..., [1, 2, 3, 0]]
    else:
        plt.close(fig)
        raise RuntimeError("Matplotlib canvas cannot export RGBA for this backend")
    rgb = rgba[..., :3]
    plt.close(fig)
    return rgb


def render_conditioning_preview(
    traj_30: np.ndarray,
    mask: np.ndarray,
    *,
    court_type: str = "nba",
    origin: str = "bottom-left",
    units: str = "ft",
    orientation: str = "h",
    figsize=(7.5, 4),
    dpi: int = STATIC_VIEW_DPI,
    showaxis: bool = False,
    court_pad_ft: float = STATIC_VIEW_PAD_FT,
) -> np.ndarray:
    """
    Court image (uint8 HxWx3) showing conditioning: for each agent, draw polyline
    through timesteps where mask[t, a] >= 0.5 (same colors as draw_trajectories_on_court).

    Always draws t=0 positions (GT) as player/ball markers on top so originals stay visible
    under traces.
    """
    traj = np.asarray(traj_30, dtype=float)
    m = np.asarray(mask, dtype=float)
    if traj.ndim != 3 or traj.shape[-1] != 2:
        raise ValueError(f"Expected traj (30, N, 2), got {traj.shape}")
    if m.shape != traj.shape[:2]:
        raise ValueError(f"mask {m.shape} must match traj time/agent dims {traj.shape[:2]}")

    _, n_ent, _ = traj.shape
    fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
    _static_view_fill_axes(fig, ax)
    court = Court(court_type=court_type, origin=origin, units=units)
    court.draw(
        ax=ax, orientation=orientation, showaxis=showaxis, pad=court_pad_ft
    )

    for a in range(n_ent):
        color = COLOR_HOME if a < 5 else COLOR_AWAY if a < 10 else COLOR_BALL
        valid = m[:, a] >= 0.5
        if not np.any(valid):
            continue
        xy = traj[valid, a, :]
        if xy.shape[0] >= 2:
            _fade_line(ax, xy, color, lw=3.0, alpha_min=0.25, alpha_max=1.0, z=4)
            _direction_arrow(
                ax,
                xy,
                color,
                lw=2.6,
                z=5,
                mutation_scale=18,
            )

    # Original t=0 positions for every agent (GT), on top of conditioning polylines.
    p_dot = 100
    b_dot = 115
    for a in range(n_ent):
        color = COLOR_HOME if a < 5 else COLOR_AWAY if a < 10 else COLOR_BALL
        z = 7 if a == 10 else 6
        ax.scatter(
            [traj[0, a, 0]],
            [traj[0, a, 1]],
            s=b_dot if a == 10 else p_dot,
            c=[color],
            edgecolors="white",
            linewidths=1.0,
            zorder=z,
        )

    fig.canvas.draw()
    if hasattr(fig.canvas, "buffer_rgba"):
        rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    elif hasattr(fig.canvas, "tostring_argb"):
        argb = np.asarray(fig.canvas.tostring_argb(), dtype=np.uint8)
        rgba = argb[..., [1, 2, 3, 0]]
    else:
        plt.close(fig)
        raise RuntimeError("Matplotlib canvas cannot export RGBA for this backend")
    rgb = rgba[..., :3]
    plt.close(fig)
    return rgb
