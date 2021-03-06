"""OctreeImage class.
"""
from ....utils.events import Event
from ..image import Image
from ._chunked_slice_data import ChunkedSliceData
from ._octree_image_slice import OctreeImageSlice


class OctreeImage(Image):
    """OctreeImage layer.

    Experimental variant of Image that renders using an Octree.

    Intended to eventually replace Image.
    """

    def __init__(self, *args, **kwargs):
        self._octree_level = None
        super().__init__(*args, **kwargs)
        self.events.add(octree_level=Event)

    @property
    def octree_level(self):
        return self._octree_level

    @octree_level.setter
    def octree_level(self, level):
        max_level = self._slice.num_octree_levels - 1
        if level > max_level:
            self._octree_level = max_level
            self.events.octree_level()  # Report we modified the request.
        else:
            self._octree_level = level
        self.refresh()  # Create new slice with this level.

    def _new_empty_slice(self):
        """Initialize the current slice to an empty image.
        """
        self._slice = OctreeImageSlice(
            self._get_empty_image(),
            self._raw_to_displayed,
            self.rgb,
            self._octree_level,
        )
        self._empty = True

    @property
    def view_chunks(self):
        """Chunks in the current slice which in currently in view."""
        return self._slice.view_chunks

    def _on_data_loaded(self, data: ChunkedSliceData, sync: bool) -> None:
        """The given data a was loaded, use it now."""
        super()._on_data_loaded(data, sync)
        self._octree_level = self._slice._octree_level

        # TODO_OCTREE: The first time _on_data_loaded() is called it's from
        # super().__init__() and the octree_level event has not been added
        # yet. So we check here. This will go away when fold OctreeImage
        # back into Image.
        has_event = hasattr(self.events, 'octree_level')

        if has_event:
            self.events.octree_level()
