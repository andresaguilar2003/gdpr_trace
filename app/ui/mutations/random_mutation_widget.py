from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel
)

from superqt import QRangeSlider


class RandomMutationWidget(QFrame):

    def __init__(
        self,
        mutation_name,
        total_traces
    ):
        super().__init__()

        self.mutation_name = mutation_name

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(mutation_name)
        )

        self.range_label = QLabel(
            f"0 - {total_traces - 1}"
        )

        layout.addWidget(
            self.range_label
        )

        self.range_slider = QRangeSlider(
            Qt.Horizontal
        )

        self.range_slider.setMinimum(0)
        self.range_slider.setMaximum(
            total_traces - 1
        )

        self.range_slider.setValue(
            (
                0,
                total_traces - 1
            )
        )

        self.range_slider.valueChanged.connect(
            self._update_label
        )

        layout.addWidget(
            self.range_slider
        )

    def _update_label(self):

        start, end = (
            self.range_slider.value()
        )

        self.range_label.setText(
            f"{start} - {end}"
        )

    def get_range(self):

        return self.range_slider.value()